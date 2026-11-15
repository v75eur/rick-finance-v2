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
            print("OK:", r.read().decode()[:300])
    except urllib.error.HTTPError as e:
        print("ERREUR:", e.read().decode()[:500])

run_sql("""
CREATE TABLE IF NOT EXISTS comptes (
  numero VARCHAR(10) PRIMARY KEY,
  libelle VARCHAR(100) NOT NULL,
  classe INT NOT NULL,
  type VARCHAR(20) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS ecritures (
  id BIGSERIAL PRIMARY KEY,
  date DATE NOT NULL,
  libelle VARCHAR(255) NOT NULL,
  compte_debit VARCHAR(10) NOT NULL REFERENCES comptes(numero),
  compte_credit VARCHAR(10) NOT NULL REFERENCES comptes(numero),
  montant NUMERIC NOT NULL CHECK (montant > 0),
  mois VARCHAR(7) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS echeances (
  id BIGSERIAL PRIMARY KEY,
  libelle VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  montant NUMERIC DEFAULT 0,
  fait BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS taches (
  id BIGSERIAL PRIMARY KEY,
  libelle VARCHAR(255) NOT NULL,
  mois VARCHAR(7) NOT NULL,
  fait BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
""", "Tables")

run_sql("""
INSERT INTO comptes (numero, libelle, classe, type) VALUES
('101','Capital',1,'passif'),('106','Reserves',1,'passif'),('120','Resultat exercice',1,'passif'),
('211','Terrains',2,'actif'),('215','Materiel',2,'actif'),('218','Amortissements',2,'actif'),
('401','Fournisseurs',4,'passif'),('411','Clients',4,'actif'),('421','Personnel',4,'passif'),
('512','Banque',5,'actif'),('530','Caisse',5,'actif'),('580','Virements internes',5,'actif'),
('601','Achats',6,'charge'),('606','Fournitures',6,'charge'),('613','Loyer',6,'charge'),
('615','Entretien',6,'charge'),('626','Transport',6,'charge'),('641','Salaires',6,'charge'),
('661','Charges financieres',6,'charge'),
('701','Ventes',7,'produit'),('706','Prestations',7,'produit'),('771','Revenus divers',7,'produit')
ON CONFLICT (numero) DO NOTHING;
""", "Comptes")

run_sql("""
ALTER TABLE comptes DISABLE ROW LEVEL SECURITY;
ALTER TABLE ecritures DISABLE ROW LEVEL SECURITY;
ALTER TABLE echeances DISABLE ROW LEVEL SECURITY;
ALTER TABLE taches DISABLE ROW LEVEL SECURITY;
""", "RLS off")

run_sql("SELECT count(*) FROM comptes;", "Verification")

print("\n=== URL ===")
print(f"https://{REF}.supabase.co")

print("\n=== ANON KEY ===")
req = urllib.request.Request(f"https://api.supabase.com/v1/projects/{REF}/api-keys")
req.add_header("Authorization", f"Bearer {TOKEN}")
try:
    with urllib.request.urlopen(req) as r:
        for k in json.loads(r.read().decode()):
            if k["name"] == "anon":
                print(k["api_key"])
except Exception as e:
    print("Erreur:", e)
