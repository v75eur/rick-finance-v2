import json, os, urllib.request, datetime, sys

# Récupère les variables d'environnement passées par GitHub Actions
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
ntfy_topic = os.environ.get('NTFY_TOPIC')

if not all([supabase_url, supabase_key, ntfy_topic]):
    print("Erreur: variables d'environnement manquantes.")
    sys.exit(1)

def fetch_table(table_name):
    url = f"{supabase_url}/rest/v1/{table_name}?select=*"
    req = urllib.request.Request(url)
    req.add_header('apikey', supabase_key)
    req.add_header('Authorization', f'Bearer {supabase_key}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Erreur lors de la lecture de {table_name}: {e}")
        sys.exit(1)

ecritures = fetch_table('ecritures')
comptes = fetch_table('comptes')

mois_actuel = datetime.date.today().strftime('%Y-%m')

def solde(numero_compte):
    s = 0.0
    for e in ecritures:
        if e['compte_debit'] == numero_compte:
            s += float(e['montant'])
        if e['compte_credit'] == numero_compte:
            s -= float(e['montant'])
    compte_info = next((c for c in comptes if c['numero'] == numero_compte), None)
    if compte_info and compte_info['type'] in ('passif', 'produit'):
        s = -s
    return s

banque = solde('512')
caisse = solde('530')
dispo = banque + caisse

# Calcule les revenus et dépenses du mois
revenus_mois = 0.0
depenses_mois = 0.0
for e in ecritures:
    if e['mois'] == mois_actuel:
        debit_info = next((c for c in comptes if c['numero'] == e['compte_debit']), None)
        credit_info = next((c for c in comptes if c['numero'] == e['compte_credit']), None)
        if credit_info and credit_info['type'] == 'produit':
            revenus_mois += float(e['montant'])
        if debit_info and debit_info['type'] == 'charge':
            depenses_mois += float(e['montant'])

message = (
    f"💰 Disponible : {dispo:,.0f} F\n"
    f"📈 Revenus {mois_actuel} : {revenus_mois:,.0f} F\n"
    f"📉 Dépenses {mois_actuel} : {depenses_mois:,.0f} F\n\n"
    f"🏦 Banque : {banque:,.0f} F\n"
    f"💵 Caisse : {caisse:,.0f} F"
).replace(',', ' ')

try:
    req = urllib.request.Request(
        f'https://ntfy.sh/{ntfy_topic}',
        data=message.encode('utf-8'),
        method='POST'
    )
    req.add_header('Title', 'Rapport Rick Finance')
    req.add_header('Tags', 'bar_chart')
    urllib.request.urlopen(req)
    print("Rapport envoyé avec succès sur ntfy.")
except Exception as e:
    print(f"Erreur lors de l'envoi à ntfy: {e}")
    sys.exit(1)
