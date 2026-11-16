import json, os, sys, urllib.request, urllib.error
REF = "dfkynusomkddxolhdtcd"
TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
if not TOKEN: print("ERREUR: token manquant"); sys.exit(1)
API = f"https://api.supabase.com/v1/projects/{REF}/database/query"
def run_sql(sql, label):
    print(f"\n=== {label} ===")
    data = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(API, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r: print("OK:", r.read().decode()[:200])
    except urllib.error.HTTPError as e: print("ERREUR:", e.read().decode()[:500])

run_sql("""
ALTER TABLE budgets_mensuels ADD COLUMN IF NOT EXISTS report_precedent NUMERIC DEFAULT 0;
ALTER TABLE echeances ADD COLUMN IF NOT EXISTS montant_paye NUMERIC DEFAULT 0;
ALTER TABLE projets ADD COLUMN IF NOT EXISTS report_mois_precedent NUMERIC DEFAULT 0;
""", "Colonnes paiement partiel")

run_sql("""
ALTER TABLE budgets_mensuels DISABLE ROW LEVEL SECURITY;
ALTER TABLE echeances DISABLE ROW LEVEL SECURITY;
ALTER TABLE projets DISABLE ROW LEVEL SECURITY;
""", "RLS off")

print("\n=== TERMINE ===")
