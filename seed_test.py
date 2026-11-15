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

# Projets de test
run_sql("""
INSERT INTO projets (nom, type, objectif, mois_debut, mois_fin) VALUES
('Terrain', 'investissement', 1000000, '2026-01', '2027-12'),
('Noel', 'epargne', 50000, '2026-11', '2026-12'),
('Fonds urgence', 'epargne', 200000, '2026-01', '2026-12')
ON CONFLICT DO NOTHING;
""", "Projets de test")

# Budget mensuel de test
run_sql("""
INSERT INTO budgets_mensuels (mois, categorie, montant_prevu) VALUES
('2026-11', 'Nourriture', 30000),
('2026-11', 'Transport', 15000),
('2026-11', 'Loyer', 50000)
ON CONFLICT (mois, categorie) DO UPDATE SET montant_prevu = EXCLUDED.montant_prevu;
""", "Budgets de test")

print("\n=== TERMINE ===")
