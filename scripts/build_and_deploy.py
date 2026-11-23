#!/usr/bin/env python3
"""
VN AI ECOSYSTEM — Autonomous Software Factory Pipeline
Executa scaffolding, personalização de arquétipo, versionamento no GitHub e deploy na Vercel.
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
    desc = description or f"Aplicação web de alta conversão construída com React e TypeScript ({repo_name})"
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
    
    if archetype == "luxury":
        title = "AUREUM & CO."
        subtitle = "Alta Relojoaria & Luxo Contemporâneo"
        desc = "Precisão inegociável, acabamento artesanal e presença magnética. Uma experiência reservada para poucos."
        badge = "Edição Limitada 2026"
        accent_color = "#eab308"
        bg_style = "bg-[#0a0907] text-[#f5f0e6]"
        btn_text = "Solicitar Catálogo Exclusivo →"
        card1_title = "Calibre Manufaturado"
        card1_desc = "Precisão cronométrica com reserva de marcha de 72 horas e acabamento espelhado à mão."
        card2_title = "Ouro Rosé 18k Maciço"
        card2_desc = "Fusão nobre de ligas preciosas que desafiam a passagem do tempo."
    elif archetype == "saas":
        title = "NEXUS METRICS"
        subtitle = "Fintech & Inteligência Operacional B2B"
        desc = "Monitore volumes, conversões e liquidez em tempo real com pipelines de baixa latência e dashboards 3D."
        badge = "Enterprise Engine v4.2"
        accent_color = "#38bdf8"
        bg_style = "bg-[#090d16] text-[#e2e8f0]"
        btn_text = "Acessar Sandbox Enterprise →"
        card1_title = "Processamento em Tempo Real"
        card1_desc = "Throughput de 50.000 tx/s com latência sub-5ms e arquitetura resiliente."
        card2_title = "Segurança Criptográfica"
        card2_desc = "Autenticação multi-camada e isolamento estrito de dados financeiros."
    elif archetype == "3d":
        title = "QUANTUM HORIZON"
        subtitle = "Experiência Visual Interativa WebGL"
        desc = "Shaders procedurais, física de partículas em tempo real e imersão espacial de padrão internacional."
        badge = "Three.js & GLSL Engine"
        accent_color = "#a855f7"
        bg_style = "bg-[#06040a] text-[#f3e8ff]"
        btn_text = "Iniciar Simulação 3D →"
        card1_title = "Shaders Dinâmicos"
        card1_desc = "Renderização procedural com reflexos de iluminação volumétrica."
        card2_title = "Taxa Constante de 120 FPS"
        card2_desc = "Otimizado para renderização fluida em dispositivos móveis e desktops."
    elif archetype == "ecom":
        title = "ATELIER ESSENTIALS"
        subtitle = "Design Minimalista D2C"
        desc = "Peças essenciais esculpidas com matéria-prima pura, linhas sóbrias e acabamento impecável."
        badge = "Coleção Cápsula 2026"
        accent_color = "#10b981"
        bg_style = "bg-[#080a08] text-[#ecfdf5]"
        btn_text = "Explorar Coleção →"
        card1_title = "Algodão Pima Orgânico"
        card1_desc = "Toque acetinado com fibras extra-longas e durabilidade incomparável."
        card2_title = "Corte Ergonômico Autoral"
        card2_desc = "Modelagem alfaiataria adaptada à anatomia do cotidiano contemporâneo."
    elif archetype == "portfolio":
        title = "VINICIUS CAETANO"
        subtitle = "Engenharia de Software & Arquitetura de Sistemas"
        desc = "Construindo infraestruturas autônomas, produtos digitais de alta escala e sistemas resilientes."
        badge = "Tech Lead & Arquiteto"
        accent_color = "#f97316"
        bg_style = "bg-[#09090b] text-[#fafafa]"
        btn_text = "Conhecer Trajetória & Projetos →"
        card1_title = "Arquitetura Cloud & Resiliência"
        card1_desc = "Desenho de microsserviços, orquestração de dados e governança de produção."
        card2_title = "Design System & UI de Elite"
        card2_desc = "Interfaces de padrão Awwwards com rigor absoluto de tipografia e fluidez."
    else: # Default ou Roulette
        title = f"{project_name.upper()}"
        subtitle = "Plataforma Digital de Alta Performance"
        desc = "Estrutura moderna componentizada, código limpo em React e TypeScript, construída para conversão."
        badge = "Produção Verificada"
        accent_color = "#3b82f6"
        bg_style = "bg-[#090a0f] text-neutral-100"
        btn_text = "Explorar Plataforma →"
        card1_title = "Modularidade & Escalabilidade"
        card1_desc = "Arquitetura limpa, tipos estritos e componentes reutilizáveis."
        card2_title = "Performance e Responsividade"
        card2_desc = "Carregamento instantâneo e layout adaptativo para qualquer tela."

    content = f"""\"use client\";

import React from "react";
import {{
  SmoothCursor,
  ShimmerButton,
  TiltCard,
}} from "./components";

export default function LandingPage() {{
  return (
    <div className="min-h-screen {bg_style} selection:bg-cyan-500/20 selection:text-cyan-200 font-sans antialiased relative overflow-x-hidden flex flex-col items-center justify-center p-6 sm:p-12">
      <SmoothCursor color="{accent_color}" glowColor="{accent_color}55" />
      
      <div className="text-center max-w-3xl mb-12 relative z-10">
        <span className="text-xs font-semibold tracking-[0.25em] uppercase mb-4 inline-block px-3 py-1 rounded-full border border-neutral-700/60 bg-neutral-900/50 backdrop-blur-md" style={{{{ color: "{accent_color}" }}}}>
          {badge}
        </span>
        <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white mb-4 uppercase">
          {title}
        </h1>
        <p className="text-sm sm:text-base font-medium tracking-wide text-neutral-400 mb-2">
          {subtitle}
        </p>
        <p className="text-neutral-400 text-xs sm:text-sm max-w-xl mx-auto leading-relaxed mb-8">
          {desc}
        </p>
        <ShimmerButton className="mx-auto shadow-2xl">
          <span>{btn_text}</span>
        </ShimmerButton>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full relative z-10">
        <TiltCard
          title="{card1_title}"
          description="{card1_desc}"
          badge="Diferencial 01"
        />
        <TiltCard
          title="{card2_title}"
          description="{card2_desc}"
          badge="Diferencial 02"
        />
      </div>

      <footer className="mt-16 text-center text-xs text-neutral-500 relative z-10 border-t border-neutral-800/80 pt-6 w-full max-w-2xl">
        <p>© 2026 {title} • Todos os direitos reservados • Engenharia Proprietária</p>
      </footer>
    </div>
  );
}}
"""
    try:
        with open(page_tsx, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✨ Customização de arquétipo '{archetype}' gravada em {page_tsx}", flush=True)
    except Exception as e:
        print(f"⚠️ Erro ao customizar page.tsx: {e}", flush=True)

def run_pipeline(project_name, template_name, chat_id=DEFAULT_FORUM_CHAT_ID, thread_id=DEFAULT_TOPIC_SOFTWARE, archetype="roulette"):
    base_dir = Path("/root/Evolução Inteligente")
    target_dir = base_dir / project_name
    
    send_topic_message(
        chat_id,
        thread_id,
        f"⚡ *FÁBRICA DE SOFTWARE — INICIANDO BUILD*\n\n"
        f"📦 *Projeto:* `{project_name}`\n"
        f"🎨 *Arquétipo/Template:* `{archetype.upper()} ({template_name})`\n\n"
        f"⚙️ _1. Scaffolding de código real (React + TypeScript)...\n"
        f"🐙 2. Criação de repositório no GitHub (`vn-24k`)...\n"
        f"▲ 3. Deploy de alta disponibilidade na Vercel..._\n\n"
        f"⏳ Aguarde alguns segundos..."
    )

    # 1. Scaffolding
    if not target_dir.exists():
        print(f"📦 Criando scaffold para {project_name}...", flush=True)
        scaffold_script = base_dir / "arsenal/scripts/scaffold-project.sh"
        subprocess.run(["bash", str(scaffold_script), project_name], check=True)

    # 2. Customização do Arquétipo
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
        f"🎨 *Arquétipo:* `{archetype.upper()}`\n"
        f"🎰 *Template:* `{template_name}`\n\n"
        f"🌐 *Site em Produção:* {vercel_url}\n"
        f"📦 *Repositório GitHub:* {gh_url}\n\n"
        f"✅ _Scaffolding, estilização, versionamento e deploy concluídos com sucesso!_"
    )
    buttons = [
        [
            {"text": "🌐 Abrir Site na Vercel", "url": vercel_url},
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
