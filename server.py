from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, os

KEY = os.environ.get("OPENROUTER_KEY", "").strip()
REPLICATE_KEY = os.environ.get("REPLICATE_KEY", "").strip()

def agent(nume, rol, mesaj):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
        json={"model": "openrouter/free", "messages": [
            {"role": "system", "content": f"Esti {nume}. {rol}. Raspunde DOAR in limba romana literara, corecta gramatical, cu diacritice corecte (ă, â, î, ș, ț). Nu folosi cuvinte straine. Fii concis, maxim 3-4 propozitii."},
            {"role": "user", "content": mesaj}
        ]}
    )
    data = r.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return "Eroare: " + str(data.get("error", {}).get("message", str(data)))

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
h1 span.t { color: #e94560; }
h1 span.s { color: #f5a623; }
h1 span.d { color: #7ed321; }
#chat { flex:1; overflow-y:auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.mesaj { padding: 10px 12px; border-radius: 16px; max-width: 92%; line-height: 1.4; font-size: 0.95em; word-break: break-word; }
.tu { background: #e94560; align-self: flex-end; border-bottom-right-radius: 4px; }
.tania { background: #0f3460; align-self: flex-start; border-left: 3px solid #e94560; border-bottom-left-radius: 4px; }
.sonia { background: #0f3460; align-self: flex-start; border-left: 3px solid #f5a623; border-bottom-left-radius: 4px; }
.delia { background: #0f3460; align-self: flex-start; border-left: 3px solid #7ed321; border-bottom-left-radius: 4px; }
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
<h1>🤖 <span class="t">Tania</span> · <span class="s">Sonia</span> · <span class="d">Delia</span></h1>
<div id="chat">
  <div class="mesaj tania"><div class="nume">🔍 Tania</div>Salut! Scrie sau vorbește o temă!</div>
  <div class="mesaj sonia"><div class="nume">✍️ Sonia</div>Eu scriu textul frumos!</div>
  <div class="mesaj delia"><div class="nume">🧐 Delia</div>Eu verific și îmbunătățesc!</div>
</div>
<div id="input-area">
  <input type="file" id="fisier" accept="image/*,.pdf,.doc,.docx,.txt,.xls,.xlsx" style="display:none" onchange="trimiseFisier()">
  <button id="atasare" onclick="document.getElementById('fisier').click()">📎</button>
  <button id="microfon" onclick="toggleVoice()" title="Apasă să vorbești">🎤</button>
  <input id="mesaj" type="text" placeholder="Scrie sau vorbește..." onkeypress="if(event.key==='Enter') trimite()">
  <button id="trimite" onclick="trimite()">Trimite ▶</button>
</div>
<script>
let recunoastere = null;
let vorbeste = false;

async function trimiseFisier() {
  const fisier = document.getElementById('fisier').files[0];
  if (!fisier) return;
  const descriere = prompt('📎 ' + fisier.name + '\n\nCe dorești să fac cu acest fișier?');
  if (!descriere) return;
  adauga('tu', 'Tu', '📎 ' + fisier.name + ' — ' + descriere);
  const t = adauga('tania', '🔍 Tania', '<span class="loading">analizează fișierul...</span>');
  const s = adauga('sonia', '✍️ Sonia', '<span class="loading">așteaptă...</span>');
  const d = adauga('delia', '🧐 Delia', '<span class="loading">așteaptă...</span>');
  const form = new FormData();
  form.append('fisier', fisier);
  const r = await fetch('/upload', {method:'POST', body: form});
  const data = await r.json();
  t.innerHTML = '<div class="nume">🔍 Tania</div>' + data.tania;
  s.innerHTML = '<div class="nume">✍️ Sonia</div>' + data.sonia;
  d.innerHTML = '<div class="nume">🧐 Delia</div>' + data.delia;
  vorbireText(data.delia);
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
  recunoastere.onresult = (e) => {
    const text = e.results[0][0].transcript;
    document.getElementById('mesaj').value = text;
    toggleVoice();
    trimite();
  };
  recunoastere.onend = () => {
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
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'ro-RO';
  utterance.rate = 1;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
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
  const t = adauga('tania', '🔍 Tania', '<span class="loading">cercetează...</span>');
  const s = adauga('sonia', '✍️ Sonia', '<span class="loading">așteaptă...</span>');
  const d = adauga('delia', '🧐 Delia', '<span class="loading">așteaptă...</span>');
  const r = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({tema})});
  const data = await r.json();
  t.innerHTML = '<div class="nume">🔍 Tania</div>' + data.tania;
  s.innerHTML = '<div class="nume">✍️ Sonia</div>' + data.sonia;
  d.innerHTML = '<div class="nume">🧐 Delia</div>' + data.delia;
  vorbireText(data.delia);
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
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            filename = self.headers.get('X-Filename', 'fisier')
            continut = f"Fisierul se numeste: {filename}. Analizeaza si descrie ce ar putea contine."
            tania = agent("Tania", "Analizezi fisiere si descrii continutul", continut)
            sonia = agent("Sonia", "Scrii despre: " + tania, continut)
            delia = agent("Delia", "Dai feedback pentru: " + sonia, continut)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"tania": tania, "sonia": sonia, "delia": delia}).encode())
            return
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tema = data['tema']
        tania = agent("Tania", "Cercetezi subiecte si dai 3 idei principale", tema)
        sonia = agent("Sonia", "Scrii texte frumoase bazate pe: " + tania, tema)
        delia = agent("Delia", "Dai feedback constructiv pentru: " + sonia, tema)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"tania": tania, "sonia": sonia, "delia": delia}).encode())

print("✅ Aplicatia porneste...")
print("📱 Deschide in browser: http://localhost:8080")
HTTPServer(('', 8080), Handler).serve_forever()
