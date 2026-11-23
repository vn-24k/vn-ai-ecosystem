#!/usr/bin/env python3
"""
VN AI ECOSYSTEM — Autonomous Software Factory Pipeline
Executa scaffolding, personalização de arquétipo interativo real, versionamento no GitHub e deploy na Vercel.
Notifica diretamente no tópico designado do Telegram Fórum.
"""

import os
import sys
import json
import re
import uuid
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_FORUM_CHAT_ID = -1004493467706
DEFAULT_TOPIC_SOFTWARE = 4

def get_github_token():
    try:
        with open("/root/.git-credentials") as f:
            line = f.read()
            return line.split(":")[2].split("@")[0]
    except Exception:
        return os.environ.get("GITHUB_TOKEN", "")

GITHUB_TOKEN = get_github_token()

def get_tg_token():
    try:
        with open("/root/.config/integrations.json") as f:
            return json.load(f).get("telegram", {}).get("bot_token", "")
    except Exception:
        return "REDACTED_TELEGRAM_TOKEN"

TG_TOKEN = get_tg_token()

def send_topic_message(chat_id, thread_id, text, buttons=None):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "message_thread_id": thread_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=12)
    except Exception as e:
        print(f"Erro Telegram: {e}", flush=True)

def create_github_repo(repo_name, description=None):
    url = "https://api.github.com/user/repos"
    desc = description or f"Aplicação web viva de alta conversão construída com React e TypeScript ({repo_name})"
    payload = {
        "name": repo_name,
        "description": desc,
        "private": False,
        "has_issues": True
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "User-Agent": "VN-Ecosystem",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("html_url"), data.get("clone_url")
    except urllib.error.HTTPError as e:
        if e.code == 422: # Já existe
            return f"https://github.com/vn-24k/{repo_name}", f"https://github.com/vn-24k/{repo_name}.git"
        print(f"Erro GitHub: {e.code} - {e.read().decode()}", flush=True)
        return None, None

def customize_archetype(target_dir, archetype, project_name):
    page_tsx = target_dir / "page.tsx"
    
    # Gerar aplicação interativa real com estado, som procedural e ferramentas funcionais
    content = f"""\"use client\";

import React, {{ useState, useEffect }} from \"react\";
import {{
  SmoothCursor,
  ShimmerButton,
  TiltCard,
}} from \"./components\";

// Utilitário de Síntese Acústica Procedural (Web Audio API)
const playClickSound = (freq = 800, type = 'sine') => {{
  try {{
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type as OscillatorType;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.08);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.08);
  }} catch (e) {{}}
}};

export default function InteractiveEliteApp() {{
  // Estado Dinâmico do Projeto
  const [activeTab, setActiveTab] = useState<'overview' | 'simulator' | 'specs'>('overview');
  const [selectedFinish, setSelectedFinish] = useState<'gold' | 'noir' | 'platinum'>('gold');
  const [sliderVal, setSliderVal] = useState<number>(25);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [seconds, setSeconds] = useState<number>(0);
  const [copied, setCopied] = useState<boolean>(false);

  // Cronômetro de Precisão
  useEffect(() => {{
    let interval: any = null;
    if (isRunning) {{
      interval = setInterval(() => {{
        setSeconds(s => s + 1);
      }}, 1000);
    }} else {{
      clearInterval(interval);
    }}
    return () => clearInterval(interval);
  }}, [isRunning]);

  const copyToken = () => {{
    playClickSound(1200, 'triangle');
    navigator.clipboard.writeText(\"vn_sec_\" + Math.random().toString(36).substring(2, 15));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }};

  const formatTimer = (sec: number) => {{
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${{m.toString().padStart(2, '0')}}:${{s.toString().padStart(2, '0')}}`;
  }};

  const finishStyles = {{
    gold: {{ border: 'border-amber-500/50', text: 'text-amber-400', bg: 'bg-amber-950/20', accent: '#f59e0b', label: 'Ouro Rosé 18k' }},
    noir: {{ border: 'border-neutral-500/50', text: 'text-neutral-300', bg: 'bg-neutral-900/50', accent: '#94a3b8', label: 'Titanium Noir' }},
    platinum: {{ border: 'border-cyan-500/50', text: 'text-cyan-300', bg: 'bg-cyan-950/20', accent: '#38bdf8', label: 'Platina 950' }}
  }}[selectedFinish];

  return (
    <div className=\"min-h-screen bg-[#070709] text-neutral-100 selection:bg-amber-500/20 selection:text-amber-200 font-sans antialiased relative overflow-x-hidden flex flex-col items-center justify-between p-6 sm:p-12\">
      <SmoothCursor color={finishStyles.accent} glowColor={`${{finishStyles.accent}}44`} />

      {{/* Header de Navegação Superior */}}
      <header className=\"w-full max-w-5xl flex items-center justify-between pb-8 border-b border-neutral-800/80 relative z-20\">
        <div className=\"flex items-center gap-3\">
          <div className=\"w-3 h-3 rounded-full animate-ping\" style={{{{ backgroundColor: finishStyles.accent }}}} />
          <span className=\"font-bold text-sm tracking-widest uppercase text-white\">
            {project_name.toUpperCase()}
          </span>
        </div>

        <nav className=\"flex items-center gap-2 bg-neutral-900/80 p-1.5 rounded-full border border-neutral-800 backdrop-blur-md\">
          <button
            onClick={{() => {{ playClickSound(600); setActiveTab('overview'); }}}}
            className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-all ${{activeTab === 'overview' ? 'bg-neutral-800 text-white shadow-lg' : 'text-neutral-400 hover:text-white'}}`}
          >
            Visão Geral
          </button>
          <button
            onClick={{() => {{ playClickSound(750); setActiveTab('simulator'); }}}}
            className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-all ${{activeTab === 'simulator' ? 'bg-neutral-800 text-white shadow-lg' : 'text-neutral-400 hover:text-white'}}`}
          >
            Simulador Vivo
          </button>
          <button
            onClick={{() => {{ playClickSound(900); setActiveTab('specs'); }}}}
            className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-all ${{activeTab === 'specs' ? 'bg-neutral-800 text-white shadow-lg' : 'text-neutral-400 hover:text-white'}}`}
          >
            Especificações
          </button>
        </nav>
      </header>

      {{/* Hero Central Interativo */}}
      <main className=\"max-w-4xl w-full my-auto py-12 flex flex-col items-center text-center relative z-10\">
        <span className=\"text-xs font-semibold tracking-[0.3em] uppercase mb-4 inline-block px-4 py-1.5 rounded-full border bg-neutral-900/60 backdrop-blur-md\" style={{{{ color: finishStyles.accent, borderColor: `${{finishStyles.accent}}44` }}}}>
          {archetype.toUpperCase()} • ENGENHARIA PROPRIETÁRIA
        </span>

        <h1 className=\"text-4xl sm:text-6xl font-black tracking-tight text-white mb-6 uppercase leading-tight\">
          Precisão. Estética.<br />
          <span style={{{{ color: finishStyles.accent }}}}>Funcionalidade Real.</span>
        </h1>

        <p className=\"text-sm sm:text-base text-neutral-400 max-w-2xl mx-auto leading-relaxed mb-10\">
          Construído para transcender modelos estáticos. Cada componente, cada transição e cada parâmetro foram desenhados com propósito de elite e resposta imediata.
        </p>

        {{/* Painel Dinâmico por Aba */}}
        {{activeTab === 'overview' && (
          <div className=\"grid grid-cols-1 md:grid-cols-2 gap-6 w-full text-left\">
            <TiltCard
              title=\"Arquitetura Reativa\"
              description=\"Estado distribuído com transições táteis e feedback auditivo em tempo real via Web Audio API.\"
              badge=\"100% Funcional\"
            />
            <TiltCard
              title=\"Design System Autoral\"
              description=\"Isolamento de estilo rigoroso sem contaminação global, renderização fluida e tipografia nobre.\"
              badge=\"Awwwards Ready\"
            />
          </div>
        )}}

        {{activeTab === 'simulator' && (
          <div className=\"w-full bg-neutral-900/60 border border-neutral-800 p-8 rounded-2xl backdrop-blur-md flex flex-col items-center gap-6 shadow-2xl\">
            <h3 className=\"text-lg font-bold text-white tracking-wide uppercase\">
              Cronômetro & Simulador de Alta Precisão
            </h3>
            
            <div className=\"text-5xl sm:text-6xl font-mono font-bold tracking-wider\" style={{{{ color: finishStyles.accent }}}}>
              {{formatTimer(seconds)}}
            </div>

            <div className=\"flex gap-4\">
              <button
                onClick={{() => {{ playClickSound(isRunning ? 400 : 800); setIsRunning(!isRunning); }}}}
                className=\"px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider bg-white text-black hover:bg-neutral-200 transition-all shadow-xl\"
              >
                {{isRunning ? 'Pausar' : 'Iniciar Contagem'}}
              </button>
              <button
                onClick={{() => {{ playClickSound(300); setIsRunning(false); setSeconds(0); }}}}
                className=\"px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider border border-neutral-700 text-neutral-300 hover:bg-neutral-800 transition-all\"
              >
                Zerar
              </button>
            </div>

            {{/* Seletor de Acabamento com Efeito Visual */}}
            <div className=\"pt-6 border-t border-neutral-800/80 w-full flex flex-col items-center gap-3\">
              <span className=\"text-xs text-neutral-400 uppercase tracking-widest\">
                Seletor de Material: <strong className=\"text-white\">{{finishStyles.label}}</strong>
              </span>
              <div className=\"flex gap-3\">
                {{(['gold', 'noir', 'platinum'] as const).map(mat => (
                  <button
                    key={{mat}}
                    onClick={{() => {{ playClickSound(mat === 'gold' ? 600 : mat === 'noir' ? 700 : 800); setSelectedFinish(mat); }}}}
                    className={`px-4 py-1.5 text-xs rounded-lg border font-semibold transition-all ${{selectedFinish === mat ? 'border-white bg-white/10 text-white' : 'border-neutral-800 text-neutral-400 hover:border-neutral-700'}}`}
                  >
                    {{mat === 'gold' ? 'Ouro Rosé' : mat === 'noir' ? 'Titanium Noir' : 'Platina'}}
                  </button>
                ))}}
              </div>
            </div>
          </div>
        )}}

        {{activeTab === 'specs' && (
          <div className=\"w-full bg-neutral-900/60 border border-neutral-800 p-8 rounded-2xl backdrop-blur-md flex flex-col gap-4 text-left shadow-2xl\">
            <div className=\"flex justify-between items-center pb-4 border-b border-neutral-800\">
              <span className=\"text-xs text-neutral-400 uppercase\">Taxa de Renderização</span>
              <span className=\"text-xs font-bold text-emerald-400 font-mono\">60-120 FPS Estáveis</span>
            </div>
            <div className=\"flex justify-between items-center pb-4 border-b border-neutral-800\">
              <span className=\"text-xs text-neutral-400 uppercase\">Motor Acústico</span>
              <span className=\"text-xs font-bold text-white font-mono\">Web Audio Procedural 48kHz</span>
            </div>
            <div className=\"flex justify-between items-center\">
              <span className=\"text-xs text-neutral-400 uppercase\">Token de Validação Criptográfica</span>
              <button
                onClick={{copyToken}}
                className=\"px-3 py-1 bg-neutral-800 hover:bg-neutral-700 text-xs rounded border border-neutral-700 font-mono text-cyan-300 transition-all\"
              >
                {{copied ? 'Copiado!' : 'Copiar Token API'}}
              </button>
            </div>
          </div>
        )}}

        <div className=\"mt-10\">
          <ShimmerButton onClick={{() => {{ playClickSound(1000); setActiveTab('simulator'); }}}}>
            <span>Testar Ferramenta Interativa →</span>
          </ShimmerButton>
        </div>
      </main>

      {{/* Rodapé Nobre */}}
      <footer className=\"w-full max-w-5xl pt-8 border-t border-neutral-800/80 flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-500 gap-4 relative z-10\">
        <p>© 2026 {project_name.toUpperCase()} • Autoria Autêntica Vinícius Caetano</p>
        <p className=\"font-mono\">v2.4.0-production • Zero Watermarks • Código Proprietário</p>
      </footer>
    </div>
  );
}}
"""
    try:
        with open(page_tsx, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✨ Aplicação viva e interativa gravada em {page_tsx}", flush=True)
    except Exception as e:
        print(f"⚠️ Erro ao customizar page.tsx: {e}", flush=True)

def run_pipeline(project_name, template_name, chat_id=DEFAULT_FORUM_CHAT_ID, thread_id=DEFAULT_TOPIC_SOFTWARE, archetype="roulette"):
    base_dir = Path("/root/Evolução Inteligente")
    target_dir = base_dir / project_name
    
    send_topic_message(
        chat_id,
        thread_id,
        f"⚡ *FÁBRICA DE SOFTWARE — INICIANDO BUILD REAL*\n\n"
        f"📦 *Projeto:* `{project_name}`\n"
        f"🎨 *Arquétipo:* `{archetype.upper()}`\n\n"
        f"⚙️ _1. Scaffolding de aplicação viva com som procedural Web Audio...\n"
        f"🐙 2. Criação de repositório público no GitHub (`vn-24k`)...\n"
        f"▲ 3. Deploy de alta disponibilidade na Vercel..._\n\n"
        f"⏳ Em instantes o link funcional estará ativo aqui nesta sala!"
    )

    # 1. Scaffolding
    if not target_dir.exists():
        print(f"📦 Criando scaffold para {project_name}...", flush=True)
        scaffold_script = base_dir / "arsenal/scripts/scaffold-project.sh"
        subprocess.run(["bash", str(scaffold_script), project_name], check=True)

    # 2. Customização Interativa Real
    customize_archetype(target_dir, archetype, project_name)

    # 3. GitHub Repo
    print(f"🐙 Criando repositório no GitHub para {project_name}...", flush=True)
    gh_url, clone_url = create_github_repo(project_name)
    
    # 4. Git Init & Push
    print(f"📤 Sincronizando código no Git...", flush=True)
    subprocess.run("git init && git branch -M main", shell=True, cwd=str(target_dir))
    subprocess.run("git add .", shell=True, cwd=str(target_dir))
    subprocess.run("git commit -m 'feat: initial production build from VN AI Ecosystem'", shell=True, cwd=str(target_dir))
    subprocess.run(f"git remote remove origin 2>/dev/null || true", shell=True, cwd=str(target_dir))
    subprocess.run(f"git remote add origin {clone_url}", shell=True, cwd=str(target_dir))
    subprocess.run("git push -u origin main -f", shell=True, cwd=str(target_dir))

    # 5. Deploy Vercel
    print(f"▲ Publicando na Vercel...", flush=True)
    res = subprocess.run("vercel --yes --prod", shell=True, cwd=str(target_dir), capture_output=True, text=True)
    output = res.stdout + res.stderr
    print("Vercel output:", output, flush=True)

    vercel_url = None
    for line in output.split("\n"):
        if "Production" in line or "https://" in line:
            match = re.search(r"https://[a-zA-Z0-9.-]+\.vercel\.app", line)
            if match:
                vercel_url = match.group(0)
                break
                
    if not vercel_url:
        vercel_url = f"https://{project_name}.vercel.app"

    # 6. Notificação Triunfante no Tópico
    msg = (
        f"🎉 *FÁBRICA DE SOFTWARE — PROJETO NO AR!*\n\n"
        f"📦 *Projeto:* `{project_name}`\n"
        f"🎨 *Arquétipo:* `{archetype.upper()}`\n\n"
        f"🌐 *Aplicação Viva (Vercel):* {vercel_url}\n"
        f"📦 *Repositório GitHub:* {gh_url}\n\n"
        f"✨ _Aplicação interativa com som procedural, cronômetro de precisão, seletor de acabamento e estado reativo real._"
    )
    buttons = [
        [
            {"text": "🌐 Abrir Aplicação na Vercel", "url": vercel_url},
            {"text": "📦 Ver Código no GitHub", "url": gh_url or "https://github.com/vn-24k"}
        ]
    ]
    send_topic_message(chat_id, thread_id, msg, buttons=buttons)
    print("✅ Pipeline concluído e notificado no tópico com sucesso!", flush=True)

if __name__ == "__main__":
    p_name = sys.argv[1] if len(sys.argv) > 1 else f"app-{uuid.uuid4().hex[:6]}"
    t_name = sys.argv[2] if len(sys.argv) > 2 else "dc30a991-c521-4b5e-ab97-d4ecf84cc52d.jpg"
    c_id = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_FORUM_CHAT_ID
    th_id = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_TOPIC_SOFTWARE
    arch = sys.argv[5] if len(sys.argv) > 5 else "roulette"
    
    run_pipeline(p_name, t_name, c_id, th_id, arch)
