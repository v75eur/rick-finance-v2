import json, os, sys, urllib.request, urllib.error

REF = "dfkynusomkddxolhdtcd"
TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
if not TOKEN:
    print("ERREUR: SUPABASE_ACCESS_TOKEN non defini"); sys.exit(1)

API = f"https://api.supabase.com/v1/projects/{REF}/database/query"

def run_sql(sql, label):
    print(f"\n=== {label} ===")
    data = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(API, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            print("OK:", r.read().decode()[:200])
    except urllib.error.HTTPError as e:
        print("ERREUR:", e.read().decode()[:500])

run_sql("""
ALTER TABLE ecritures ADD COLUMN IF NOT EXISTS type_operation VARCHAR(20) DEFAULT 'depense';
ALTER TABLE ecritures ADD COLUMN IF NOT EXISTS projet_id BIGINT;
""", "Ajout colonnes a ecritures")

run_sql("""
CREATE TABLE IF NOT EXISTS budgets_mensuels (
  id BIGSERIAL PRIMARY KEY,
  mois VARCHAR(7) NOT NULL,
  categorie VARCHAR(50) NOT NULL,
  montant_prevu NUMERIC NOT NULL,
  UNIQUE(mois, categorie)
);
CREATE TABLE IF NOT EXISTS projets (
  id BIGSERIAL PRIMARY KEY,
  nom VARCHAR(100) NOT NULL,
  type VARCHAR(20) NOT NULL DEFAULT 'epargne',
  objectif NUMERIC NOT NULL DEFAULT 0,
  mois_debut VARCHAR(7),
  mois_fin VARCHAR(7),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS historique_mensuel (
  id BIGSERIAL PRIMARY KEY,
  mois VARCHAR(7) UNIQUE NOT NULL,
  total_produits NUMERIC DEFAULT 0,
  total_charges NUMERIC DEFAULT 0,
  resultat NUMERIC DEFAULT 0,
  solde_banque NUMERIC DEFAULT 0,
  solde_caisse NUMERIC DEFAULT 0,
  patrimoine NUMERIC DEFAULT 0,
  epargne_cumulee NUMERIC DEFAULT 0,
  cloture_le TIMESTAMPTZ DEFAULT NOW()
);
""", "Creation des 3 nouvelles tables")

run_sql("""
ALTER TABLE budgets_mensuels DISABLE ROW LEVEL SECURITY;
ALTER TABLE projets DISABLE ROW LEVEL SECURITY;
ALTER TABLE historique_mensuel DISABLE ROW LEVEL SECURITY;
""", "RLS off")

run_sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;", "Verification tables")

print("\n=== TERMINE ===")
