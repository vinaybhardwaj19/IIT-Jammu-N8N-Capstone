import requests

s = requests.Session()
login_url = 'http://localhost:5678/rest/login'
r = s.post(login_url, json={'emailOrLdapLoginId': 'vinaybhardwaj3230@gmail.com', 'password': 'Vinay@123'})
wf_resp = s.get('http://localhost:5678/rest/workflows')
print('Workflows status:', wf_resp.status_code)
data = wf_resp.json()
wfs = data.get('data', [])
print(f'Retrieved {len(wfs)} workflows from n8n API:')
for w in wfs:
    clean_name = str(w.get('name')).encode('ascii', errors='replace').decode('ascii')
    print('  ID:', w.get('id'), '| Active:', w.get('active'), '| Name:', clean_name)
