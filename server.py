from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, os

KEY = os.environ.get("OPENROUTER_KEY", "").strip()

def agent(rol_sistem, mesaj):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
        json={
            "model": "openrouter/free",
            "messages": [
                {"role": "system", "content": rol_sistem},
                {"role": "user", "content": mesaj}
            ]
        }
    )
    data = r.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return ""

def manager_ai(tema):
    # Agent 1 - Cercetare
    cercetare = agent(
        "Esti un expert cercetator. Raspunde EXCLUSIV in limba romana corecta. Cerceteaza si ofera 3 idei cheie despre subiect. Fii concis.",
        tema
    )
    # Agent 2 - Redactare
    redactare = agent(
        "Esti un redactor expert. Raspunde EXCLUSIV in limba romana corecta. Transforma aceste idei intr-un raspuns clar si coerent pentru utilizator. Fii concis.",
        "Idei: " + cercetare + "\nSubiect: " + tema
    )
    # Agent Manager - Sintetizeaza
    raspuns_final = agent(
        "Esti un Manager AI expert. Raspunde EXCLUSIV in limba romana corecta, cu diacritice. Sintetizeaza informatia intr-un singur raspuns clar, util si prietenos pentru utilizator. Maximum 4-5 propozitii.",
        "Informatii: " + redactare + "\nIntrebarea utilizatorului: " + tema
    )
    return raspuns_final

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Echipa AI</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: Arial; background: #1a1a2e; color: white; height: 100dvh; display: flex; flex-direction: column; font-size: 16px; }
h1 { text-align:center; padding: 12px; background: #16213e; font-size: 1.1em; border-bottom: 1px solid #333; }
h1 span { color: #e94560; }
#chat { flex:1; overflow-y:auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.mesaj { padding: 10px 12px; border-radius: 16px; max-width: 92%; line-height: 1.5; font-size: 0.95em; word-break: break-word; }
.tu { background: #e94560; align-self: flex-end; border-bottom-right-radius: 4px; }
.manager { background: #0f3460; align-self: flex-start; border-left: 4px solid #e94560; border-bottom-left-radius: 4px; }
.nume { font-weight: bold; font-size: 0.75em; margin-bottom: 4px; opacity: 0.85; }
#input-area { display: flex; padding: 10px; gap: 8px; background: #16213e; border-top: 1px solid #333; align-items: center; }
#mesaj { flex:1; padding: 12px 15px; border-radius: 25px; border: none; background: #0f3460; color: white; font-size: 1em; outline: none; }
#mesaj::placeholder { color: #aaa; }
#trimite { padding: 12px 18px; border-radius: 25px; border: none; background: #e94560; color: white; cursor: pointer; font-size: 1em; }
#microfon { padding: 12px; border-radius: 50%; border: none; background: #0f3460; color: white; cursor: pointer; font-size: 1.2em; width: 48px; height: 48px; }
#microfon.activ { background: #e94560; animation: pulse 1s infinite; }
#atasare { padding: 12px; border-radius: 50%; border: none; background: #0f3460; color: white; cursor: pointer; font-size: 1.2em; width: 48px; height: 48px; }
@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
.loading { opacity: 0.6; font-style: italic; }
</style>
</head>
<body>
<h1>🤖 <span>Manager AI</span></h1>
<div id="chat">
  <div class="mesaj manager"><div class="nume">🧠 Manager AI</div>Salut! Cum te pot ajuta astazi? Scrie sau vorbeste!</div>
</div>
<div id="input-area">
  <input type="file" id="fisier" accept="image/*,.pdf,.doc,.docx,.txt,.xls,.xlsx" style="display:none" onchange="trimiseFisier()">
  <button id="atasare" onclick="document.getElementById('fisier').click()">📎</button>
  <button id="microfon" onclick="toggleVoice()" title="Apasa sa vorbesti">🎤</button>
  <input id="mesaj" type="text" placeholder="Scrie sau vorbeste..." onkeypress="if(event.key==='Enter') trimite()">
  <button id="trimite" onclick="trimite()">Trimite</button>
</div>
<script>
let recunoastere = null;
let vorbeste = false;

async function trimiseFisier() {
  const fisier = document.getElementById('fisier').files[0];
  if (!fisier) return;
  const input = document.getElementById('mesaj');
  input.value = '📎 ' + fisier.name + ' — ';
  input.focus();
  window.fisierSelectat = fisier;
}

function initVoice() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    document.getElementById('microfon').style.display = 'none';
    return;
  }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recunoastere = new SR();
  recunoastere.lang = 'ro-RO';
  recunoastere.continuous = false;
  recunoastere.interimResults = false;
  recunoastere.onresult = function(e) {
    const text = e.results[0][0].transcript;
    document.getElementById('mesaj').value = text;
    toggleVoice();
    trimite();
  };
  recunoastere.onend = function() {
    vorbeste = false;
    document.getElementById('microfon').classList.remove('activ');
    document.getElementById('microfon').textContent = '🎤';
  };
}

function toggleVoice() {
  if (!recunoastere) return;
  if (vorbeste) {
    recunoastere.stop();
    vorbeste = false;
    document.getElementById('microfon').classList.remove('activ');
    document.getElementById('microfon').textContent = '🎤';
  } else {
    recunoastere.start();
    vorbeste = true;
    document.getElementById('microfon').classList.add('activ');
    document.getElementById('microfon').textContent = '🔴';
  }
}

function vorbireText(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'ro-RO';
  u.rate = 1;
  u.pitch = 1;
  window.speechSynthesis.speak(u);
}

function adauga(clasa, nume, text) {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'mesaj ' + clasa;
  div.innerHTML = '<div class="nume">' + nume + '</div>' + text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

async function trimite() {
  const input = document.getElementById('mesaj');
  const tema = input.value.trim();
  if (!tema) return;
  input.value = '';
  adauga('tu', 'Tu', tema);
  const m = adauga('manager', '🧠 Manager AI', '<span class="loading">lucreaza...</span>');

  if (window.fisierSelectat) {
    const fisier = window.fisierSelectat;
    window.fisierSelectat = null;
    const reader = new FileReader();
    reader.onload = async function(e) {
      const base64 = e.target.result.split(',')[1];
      const tip = fisier.type;
      const r = await fetch('/chat-imagine', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({tema: tema, base64: base64, tip: tip})
      });
      const data = await r.json();
      m.innerHTML = '<div class="nume">🧠 Manager AI</div>' + data.raspuns;
      vorbireText(data.raspuns);
    };
    reader.readAsDataURL(fisier);
    return;
  }

  const r = await fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({tema: tema})
  });
  const data = await r.json();
  m.innerHTML = '<div class="nume">🧠 Manager AI</div>' + data.raspuns;
  vorbireText(data.raspuns);
}

initVoice();
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path == '/chat-imagine':
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            tema = data['tema']
            base64_img = data['base64']
            tip = data['tip']
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
                json={
                    "model": "openrouter/free",
                    "messages": [
                        {"role": "user", "content": [
                            {"type": "image_url", "image_url": {"url": "data:" + tip + ";base64," + base64_img}},
                            {"type": "text", "text": "Esti Manager AI. " + tema + ". Raspunde exclusiv in limba romana corecta, concis si clar."}
                        ]}
                    ]
                }
            )
            result = r.json()
            if "choices" in result:
                raspuns = result["choices"][0]["message"]["content"]
            else:
                raspuns = "Eroare la procesarea imaginii."
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"raspuns": raspuns}).encode())
            return

        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tema = data['tema']
        raspuns = manager_ai(tema)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"raspuns": raspuns}).encode())

print("Aplicatia porneste...")
print("Deschide in browser: http://localhost:8080")
HTTPServer(('', 8080), Handler).serve_forever()
