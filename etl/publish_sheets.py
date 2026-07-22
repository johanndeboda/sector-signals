"""
publish_sheets.py — aggregate the current daily snapshot + TTM financials into
two pre-aggregated frames and (stage 4) push them to the Google Sheet that
Tableau Public auto-refreshes.

Runs headless in GitHub Actions AFTER load_hiring.py, behind the completeness
guard (a partial scrape must not publish a partial dashboard). Neon creds + the
service-account JSON arrive as repo secrets in CI; load_dotenv() populates them
locally and is a harmless no-op in CI.

Two tabs, one per data SHAPE (Day-16 decision):
  signals  — one row per ticker (wide): scalar per-ticker features
  role_mix — one row per ticker-per-bucket (long): feeds the heatmap tile
Overwrite daily, never append: Neon is the archive, the Sheet is a 9-row window.
"""
import json
import gspread
import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

# ── 1. connect (Neon idle-drop-safe: pre-ping + recycle) ────────────────────
load_dotenv(override=True)
engine = create_engine(
    f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}",
    pool_pre_ping=True,
    pool_recycle=300,
)
pd.read_sql("SELECT 1 AS ok", engine)

# ── 2. current hiring snapshot (date carried IN the data, not just the WHERE) ─
df = pd.read_sql("""
    SELECT snapshot_date, ticker, title
    FROM hiring_signals
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM hiring_signals)
""", engine)
assert df["snapshot_date"].nunique() == 1, "expected exactly one snapshot date"
SNAP_DATE = df["snapshot_date"].iloc[0]
print(f"snapshot {SNAP_DATE} | {df['ticker'].nunique()} tickers | {len(df):,} postings")



# ── 3. classifier — COPIED VERBATIM from 03_hiring_category.ipynb (Cell 6) ──
#     Third copy (also in 20_cross_signals.ipynb). NOT extracted to a module, by
#     decisions. The reconcile print below is the drift
#     detector — if unclassified/AI % diverge from 03, a copy went stale.
AI_PAT = re.compile(r"\b(ai|ml|machine learning|deep learning|neural|llm|large language model|generative|genai|computer vision|nlp|natural language|transformer|reinforcement learning)\b")

ROLE_RULES = [
    ("Product Management",        r"\b(product manager|product management|product owner|head of product|director of product)\b"),
    ("Program / Project Mgmt",    r"\b(program manager|project manager|technical program|tpm|scrum master|release manager|agile)\b"),
    ("Sales / Field / Marketing", r"\b(application engineer|applications engineer|field application|solution architect|solutions architect|solutions engineer|sales|account manager|account executive|account director|business development|customer success|field engineer|presales|marketing|developer relations|client manager|enablement)\b"),
    ("Data & Analytics",          r"\b(data scientist|data engineer|data analyst|analytics|business intelligence)\b"),
    ("Corporate / Ops / G&A",     r"\b(accountant|accounting|finance|financial|controller|human resources|hr|employee relations|recruit|talent acquisition|legal|counsel|paralegal|facilities|supply chain|supply management|procurement|sourcing|supplier management|supplier manager|buyer|purchasing|payroll|logistics|operations|cost control|business analyst|program analyst|it support|help desk|administrative|executive assistant|corporate communications)\b"),
    ("Research / Science",        r"\b(research scientist|researcher|scientist|applied scientist|principal scientist|research engineer|post-doc|postdoc|post doc)\b"),
    ("Verification & Validation", r"\b(verification|validation|formal verification|emulation)\b"),
    ("Software & Firmware",       r"\b(software|firmware|embedded|device driver|sdk|kernel|compiler|full stack|fullstack|developer|devops|site reliability)\b"),
    ("Manufacturing & Process",   r"\b(process|equipment|manufacturing|fab|hvm|yield|packaging|assembly|technician|reliability|failure analysis|test engineer|production|industrial|quality|supplier quality|mechanical|mfg|product engineer|product development|module|npi|amhs)\b"),
    ("Design (silicon/IC)",       r"\b(design|designer|analog|mixed signal|mixed-signal|rtl|layout|asic|soc|silicon|chip|dft|vlsi|circuit|standard cell|cad)\b"),
    ("Systems & Architecture",    r"\b(systems|system engineer|architect|architecture|integration|signal integrity|performance|hardware|board)\b"),
    ("Engineering (unspecified)", r"\b(engineer|engineering)\b"),
    ("Management (general)",      r"\b(manager|mgr|director|management|head of|vice president|vp|chief|supervisor)\b"),
]
ROLE_RULES = [(name, re.compile(pat)) for name, pat in ROLE_RULES]

def classify_role(title):
    t = title.lower()
    for name, pat in ROLE_RULES:
        if pat.search(t):
            return name
    return "Other / Unclassified"

df["role_bucket"] = df["title"].fillna("").apply(classify_role)
df["is_ai"]       = df["title"].fillna("").apply(lambda t: bool(AI_PAT.search(t.lower())))

print(f"reconcile | unclassified {(df['role_bucket']=='Other / Unclassified').mean():.1%} "
      f"| AI-flagged {df['is_ai'].mean():.1%} ({int(df['is_ai'].sum())} jobs)")

# ── 4. per-ticker hiring features ───────────────────────────────────────────
ai = df.groupby("ticker")["is_ai"].agg(ai_jobs="sum", n_jobs="count")
ai["ai_pct"] = (ai["ai_jobs"] / ai["n_jobs"] * 100).round(1)
ai = ai.sort_values("ai_pct", ascending=False)

mix = pd.crosstab(df["ticker"], df["role_bucket"], normalize="index").mul(100).round(1)
mix = mix[df["role_bucket"].value_counts().index]   # columns ordered by overall size
print(f"mix shape {mix.shape}  ({mix.shape[1]} buckets)")

# ── 5. financials → trailing-4-quarter (TTM), revenue-weighted ──────────────
fin = pd.read_sql("SELECT * FROM financials_quarterly ORDER BY ticker, quarter", engine)
fin["quarter"] = pd.to_datetime(fin["quarter"])
HIRING_TICKERS = ["AMD","AVGO","CDNS","INTC","MRVL","MU","NVDA","QCOM","TXN"]
core = fin[fin["ticker"].isin(HIRING_TICKERS)].sort_values(["ticker","quarter"]).copy()

last4 = core.groupby("ticker").tail(4).copy()
chk = last4.groupby("ticker").agg(
    q=("quarter", "size"),
    rev_na=("revenue",          lambda s: s.isna().sum()),
    rd_na=("rd_spend",          lambda s: s.isna().sum()),
    om_na=("operating_margin",  lambda s: s.isna().sum()),
)
print("\nTTM window (want q=4, all *_na=0):"); print(chk.to_string())

last4["op_income"] = last4["operating_margin"] * last4["revenue"]   # margin stored as a fraction
g = last4.groupby("ticker")
rev_rd = last4.loc[last4["rd_spend"].notna()].groupby("ticker")["revenue"].sum()  # match rev to R&D availability
fin_ttm = pd.DataFrame({
    "rd_intensity":     g["rd_spend"].sum() / rev_rd,
    "rd_qtrs":          g["rd_spend"].apply(lambda s: s.notna().sum()),
    "operating_margin": g["op_income"].sum() / g["revenue"].sum(),
})
print("\nfin_ttm:"); print(fin_ttm.round(3).to_string())

# ── 6. assemble the two Sheet frames (numpy→python conversion happens at write, stage 4) ─
SEGMENT = {"NVDA":"Fabless","AMD":"Fabless","QCOM":"Fabless","AVGO":"Fabless","MRVL":"Fabless",
           "INTC":"IDM","MU":"IDM","TXN":"IDM","CDNS":"EDA"}

# WIDE — one row per ticker, scalars only. Fractions → *_pct here (the Sheet is a
# surface someone may open directly; notebooks keep fractions to match 10_financials).
signals = (
    ai[["n_jobs", "ai_pct"]]
    .join(fin_ttm)
    .assign(
        segment              = lambda d: d.index.map(SEGMENT),
        rd_intensity_pct     = lambda d: (d["rd_intensity"] * 100).round(1),
        operating_margin_pct = lambda d: (d["operating_margin"] * 100).round(1),
        snapshot_date        = str(SNAP_DATE),
    )
    .reset_index()                       # ticker index → a real column
    .loc[:, ["ticker", "segment", "n_jobs", "ai_pct",
             "rd_intensity_pct", "rd_qtrs", "operating_margin_pct", "snapshot_date"]]
)

# LONG — one row per ticker-per-bucket, for the heatmap tile.
role_mix = (
    mix.reset_index()                    # ticker index → column
       .melt(id_vars="ticker", var_name="role_bucket", value_name="pct")
       .assign(snapshot_date=str(SNAP_DATE))
       .sort_values(["ticker", "role_bucket"], ignore_index=True)
)

print(f"\nsignals  {signals.shape}")
print(signals.to_string(index=False))
print(f"\nrole_mix {role_mix.shape}  (expect 126 = 9×14)")
print(role_mix.head(14).to_string(index=False))
print("… (one ticker's 14 buckets shown; 8 more follow)")

# ── 7. authenticate as the service account (secret in CI, file locally) ─────
SHEET_ID = "1i-4Mj3GcT2AF0rawXuely5DjRBjKJ7cpjGDjiSdYV_Y"   # same Sheet testsheets.py proved

raw = os.environ.get("GOOGLE_SA_JSON")                 # CI: GitHub injects the secret as a string
if raw:
    creds = json.loads(raw)
else:                                                  # local: read the gitignored file directly
    with open("sector_signals_GCP_SA_key.json") as f:  #   (fixed path — no session env var to drop)
        creds = json.load(f)

gc = gspread.service_account_from_dict(creds)
sh = gc.open_by_key(SHEET_ID)
print(f"\nopened '{sh.title}'  | existing tabs: {[w.title for w in sh.worksheets()]}")

# ── 8. write each frame to its tab — overwrite daily, never append ──────────
def write_tab(sh, title, df):
    """Overwrite `title` with header + rows; create the tab if it doesn't exist yet.
    numpy scalars (int64/float64) aren't JSON-serializable → cast to Python natives."""
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=len(df) + 10, cols=len(df.columns) + 2)
    values = [df.columns.tolist()] + [
        [None if pd.isna(x) else (x.item() if hasattr(x, "item") else x) for x in row]
        for row in df.itertuples(index=False, name=None)
    ]
    ws.clear()
    ws.update(values, "A1")                            # gspread 6.x: values FIRST, then range
    print(f"  wrote {title:9} {df.shape[0]:>3} rows × {df.shape[1]} cols")

print("writing tabs:")
write_tab(sh, "signals",  signals)
write_tab(sh, "role_mix", role_mix)
print(f"\ndone — Sheet updated for snapshot {SNAP_DATE}")