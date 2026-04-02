from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("OPENROUTER_API_KEY")

def agent(nume, rol, mesaj):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"model": "openrouter/free", "messages": [
            {"role": "system", "content": f"Esti {nume}. {rol}. Vorbesti romaneste. Maxim 3 propozitii."},
            {"role": "user", "content": mesaj}
        ]}
    )
    return r.json()["choices"][0]["message"]["content"]

HTML = """
<!DOCTYPE html>
<html>
<head><title>Echipa AI</title></head>
<body>
<h1>Echipa AI - Tania, Sonia, Delia</h1>
<div id="chat"></div>
<input id="mesaj" type="text" placeholder="Scrie aici">
<button onclick="trimite()">Trimite</button>
<script>
async function trimite() {
    let tema = document.getElementById('mesaj').value;
    let r = await fetch('/chat', {method:'POST', body:JSON.stringify({tema}), headers:{'Content-Type':'application/json'}});
    let data = await r.json();
    document.getElementById('chat').innerHTML = 
        '<b>Tu:</b> ' + tema + '<br>' +
        '<b>Tania:</b> ' + data.tania + '<br>' +
        '<b>Sonia:</b> ' + data.sonia + '<br>' +
        '<b>Delia:</b> ' + data.delia;
}
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML.encode())
    
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        tema = data['tema']
        tania = agent("Tania", "Cerceteaza", tema)
        sonia = agent("Sonia", "Scrie frumos", tania)
        delia = agent("Delia", "Da feedback", sonia)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"tania": tania, "sonia": sonia, "delia": delia}).encode())

print("Server pe http://localhost:8080")
HTTPServer(('', 8080), Handler).serve_forever()