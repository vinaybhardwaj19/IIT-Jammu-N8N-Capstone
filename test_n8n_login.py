import requests

s = requests.Session()
login_url = "http://localhost:5678/rest/login"
payload = {
    "emailOrLdapLoginId": "vinaybhardwaj3230@gmail.com",
    "password": "Vinay@123"
}
r = s.post(login_url, json=payload, timeout=10)
print('Login response status:', r.status_code)
print('Login response:', r.text[:300])
print('Session cookies:', s.cookies.get_dict())
