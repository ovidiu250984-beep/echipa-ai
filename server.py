from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, os

KEY = os.environ.get("OPENROUTER_KEY", "").strip()

AGENTI = {
    "voluntari": {
        "nume": "Agent Voluntari & Outreach",
        "rol": "Ești expert în recrutare voluntari, comunicare cu comunitatea și coordonare echipe pentru ONG-uri caritabile. Ajuți cu: recrutare voluntari, mesaje comunitate, coordonare echipe, motivare voluntari."
    },
    "fundraising": {
        "nume": "Agent Fundraising",
        "rol": "Ești expert în strângere de fonduri pentru ONG-uri. Ajuți cu: strategii fundraising, propuneri de sponsorizare, campanii donații, cereri de finanțare, relații cu donatori."
    },
    "social_media": {
        "nume": "Agent Content & Social Media",
        "rol": "Ești expert în comunicare digitală pentru ONG-uri. Ajuți cu: postări Facebook și Instagram, comunicate de presă, newsletter, campanii online, storytelling caritabil."
    },
    "parteneriate": {
        "nume": "Agent Parteneriate",
        "rol": "Ești expert în parteneriate pentru ONG-uri. Ajuți cu: colaborări DGASPC, parteneriate cu primării, relații cu firme sponsor, colaborări cu alte ONG-uri, protocoale de colaborare."
    },
    "proiecte": {
        "nume": "Agent Project & Event Manager",
        "rol": "Ești expert în managementul proiectelor și evenimentelor caritabile. Ajuți cu: planificare evenimente, liste de sarcini, termene limită, coordonare proiecte, organizare activități."
    },
    "documente": {
        "nume": "Agent Rapoarte & Documente",
        "rol": "Ești expert în documentație pentru ONG-uri. Ajuți cu: rapoarte pentru finanțatori, documente ANAF, procese verbale, minute ședințe, rapoarte de activitate, cereri și adrese oficiale."
    },
    "legal": {
        "nume": "Agent Legal & Conformitate",
        "rol": "Ești expert în legislația ONG-urilor din România. Ajuți cu: legislație ONG, contracte voluntari, conformitate GDPR, regulamente interne, obligații legale, statut asociație."
    },
    "monitorizare": {
        "nume": "Agent Monitorizare & Impact",
        "rol": "Ești expert în măsurarea impactului social. Ajuți cu: statistici activități, rapoarte de impact, indicatori de performanță, evaluare progres, rapoarte pentru sponsori."
    },
    "comunicare": {
        "nume": "Agent Comunicare & PR",
        "rol": "Ești expert în relații publice pentru ONG-uri. Ajuți cu: comunicate presă, relații cu media, scrisori oficiale, discursuri, prezentări publice, imagine organizație."
    }
}

INSTRUCTIUNI_ROMANA = "Raspunde EXCLUSIV in limba romana corecta, cu diacritice (ă, â, î, ș, ț). Fii concis, clar si prietenos. Maximum 5 propozitii."

def apeleaza_agent(rol_agent, mesaj):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
        json={
            "model": "openrouter/free",
            "messages": [
                {"role": "system", "content": rol_agent + " " + INSTRUCTIUNI_ROMANA},
                {"role": "user", "content": mesaj}
            ]
        }
    )
    data = r.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return ""

def manager_ai(tema):
    # Pasul 1: Manager decide care agent e potrivit
    lista_agenti = ", ".join(AGENTI.keys())
    decizie = apeleaza_agent(
        "Esti Manager AI pentru o asociatie caritabila. Analizezi cererea si decizi care agent specializat este cel mai potrivit. Raspunzi DOAR cu numele cheii agentului, nimic altceva. Agenti disponibili: " + lista_agenti,
        "Cerere: " + tema + "\nRaspunde DOAR cu cheia agentului potrivit (ex: fundraising, voluntari, social_media etc)"
    )
    
    # Curata raspunsul
    agent_ales = decizie.strip().lower().replace(" ", "_")
    
    # Verifica daca agentul exista
    agent_valid = None
    for cheie in AGENTI.keys():
        if cheie in agent_ales:
            agent_valid = cheie
            break
    
    # Daca nu a gasit un agent valid, foloseste primul potrivit
    if not agent_valid:
        agent_valid = "voluntari"
    
    agent_info = AGENTI[agent_valid]
    
    # Pasul 2: Agentul specializat proceseaza cererea
    raspuns_agent = apeleaza_agent(
        agent_info["rol"],
        tema
    )
    
    # Pasul 3: Manager sintetizeaza raspunsul final
    raspuns_final = apeleaza_agent(
        "Esti Manager AI pentru o asociatie caritabila. Primesti raspunsul unui agent specializat si il prezinti utilizatorului intr-un mod clar, profesional si prietenos. Mentionezi pe scurt de la ce expert vine informatia. " + INSTRUCTIUNI_ROMANA,
        "Agentul " + agent_info["nume"] + " a raspuns: " + raspuns_agent + "\nCererea initiala: " + tema
    )
    
    return raspuns_final, agent_info["nume"]

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Manager AI - Asociatie Caritabila</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: Arial; background: #1a1a2e; color: white; height: 100dvh; display: flex; flex-direction: column; font-size: 16px; }
h1 { text-align:center; padding: 12px; background: #16213e; font-size: 1em; border-bottom: 1px solid #333; }
h1 span { color: #e94560; }
h1 small { display:block; font-size:0.7em; color:#aaa; margin-top:2px; }
#chat { flex:1; overflow-y:auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.mesaj { padding: 10px 12px; border-radius: 16px; max-width: 92%; line-height: 1.5; font-size: 0.95em; word-break: break-word; }
.tu { background: #e94560; align-self: flex-end; border-bottom-right-radius: 4px; }
.manager { background: #0f3460; align-self: flex-start; border-left: 4px solid #e94560; border-bottom-left-radius: 4px; }
.agent-tag { display:inline-block; background: #e94560; color: white; font-size: 0.65em; padding: 2px 8px; border-radius: 10px; margin-bottom: 6px; }
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
<h1>🤖 <span>Manager AI</span><small>Asociatie Caritabila • 9 Agenti Specializati</small></h1>
<div id="chat">
  <div class="mesaj manager">
    <div class="nume">🧠 Manager AI</div>
    Salut! Sunt Manager-ul tau AI pentru asociatia caritabila. Am 9 agenti specializati gata sa te ajute cu: voluntari, fundraising, social media, parteneriate, proiecte, documente, legal, monitorizare si comunicare PR. Cum te pot ajuta astazi?
  </div>
</div>
<div id="input-area">
  <input type="file" id="fisier" accept="image/*,.pdf,.doc,.docx,.txt,.xls,.xlsx" style="display:none" onchange="trimiseFisier()">
  <button id="atasare" onclick="document.getElementById('fisier').click()">📎</button>
  <button id="microfon" onclick="toggleVoice()" title="Apasa sa vorbesti">🎤</button>
  <input id="mesaj" type="text" placeholder="Ex: Scrie o postare Facebook..." onkeypress="if(event.key==='Enter') trimite()">
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
  const m = adauga('manager', '🧠 Manager AI', '<span class="loading">deleghez catre agentul potrivit...</span>');

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
      m.innerHTML = '<div class="nume">🧠 Manager AI</div><span class="agent-tag">' + data.agent + '</span><br>' + data.raspuns;
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
  m.innerHTML = '<div class="nume">🧠 Manager AI</div><span class="agent-tag">' + data.agent + '</span><br>' + data.raspuns;
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
                            {"type": "text", "text": "Esti Manager AI pentru o asociatie caritabila. " + tema + ". Raspunde exclusiv in limba romana corecta, concis si clar."}
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
            self.wfile.write(json.dumps({"raspuns": raspuns, "agent": "Agent Vizual"}).encode())
            return

        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tema = data['tema']
        raspuns, agent_nume = manager_ai(tema)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"raspuns": raspuns, "agent": agent_nume}).encode())

print("Aplicatia porneste...")
print("Deschide in browser: http://localhost:8080")
HTTPServer(('', 8080), Handler).serve_forever()
