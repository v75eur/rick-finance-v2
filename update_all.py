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
ALTER TABLE projets ADD COLUMN IF NOT EXISTS priorite INT DEFAULT 1;
ALTER TABLE projets ADD COLUMN IF NOT EXISTS epargne_mensuelle_prevue NUMERIC DEFAULT 0;
ALTER TABLE projets ADD COLUMN IF NOT EXISTS rang INT DEFAULT 0;
""", "Colonnes projets")

run_sql("""
CREATE TABLE IF NOT EXISTS dettes (
  id BIGSERIAL PRIMARY KEY,
  type VARCHAR(20) NOT NULL DEFAULT 'dette',
  nom VARCHAR(100) NOT NULL,
  montant NUMERIC NOT NULL DEFAULT 0,
  montant_restant NUMERIC NOT NULL DEFAULT 0,
  date_echeance DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE dettes DISABLE ROW LEVEL SECURITY;
""", "Table dettes")

print("\n=== TERMINE ===")
