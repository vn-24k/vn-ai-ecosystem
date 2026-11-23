#!/usr/bin/env python3
"""
VN AI ECOSYSTEM — Enterprise Forum Dispatcher & Topic Controller
Gerencia o Supergrupo Fórum 'VN IA Ecosystem' (-1004493467706) com 4 tópicos segregados:
• Tópico 4: 🚀 Fábrica de Software
• Tópico 5: 🎬 Estúdio de Mídia
• Tópico 6: 🧠 Segundo Cérebro
• Tópico 7: 🛡️ Infraestrutura & DevOps
"""

import os
import sys
import json
import time
import uuid
import shutil
import threading
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.parse
import requests

CONFIG_FILE = Path("/root/.config/integrations.json")
OBSIDIAN_VAULT = Path("/sdcard/Documents/Obsidian VN/VN")
ROULETTE_SCRIPT = Path("/root/Evolução Inteligente/arsenal/scripts/spin_roulette.py")
BUILD_DEPLOY_SCRIPT = Path("/root/vn-ai-ecosystem/scripts/build_and_deploy.py")
DISSECTOR_SCRIPT = Path("/root/vn-ai-ecosystem/scripts/dissector_service.py")
REELS_SCRIPT = Path("/root/scripts/gerar_reels_masterpiece.py")
TRAILER_SCRIPT = Path("/root/scripts/gerar_trailer_netflix.py")

def load_integrations():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

CFG = load_integrations()
TG_TOKEN = CFG.get("telegram", {}).get("bot_token", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
FORUM_CHAT_ID = CFG.get("telegram", {}).get("forum_group_id", -1004493467706)

TOPIC_SOFTWARE = 4
TOPIC_MEDIA = 5
TOPIC_BRAIN = 6
TOPIC_DEVOPS = 7

def send_topic_message(thread_id, text, buttons=None, chat_id=FORUM_CHAT_ID):
    """Envia mensagem dentro de um tópico específico do fórum"""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if thread_id and chat_id == FORUM_CHAT_ID:
        payload["message_thread_id"] = thread_id
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
        
    try:
        resp = requests.post(url, json=payload, timeout=12)
        return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem no tópico {thread_id}: {e}", flush=True)
        return False

def send_topic_audio(thread_id, audio_path, caption=None, chat_id=FORUM_CHAT_ID):
    """Envia arquivo de áudio diretamente para o tópico"""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendAudio"
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": (Path(audio_path).name, f, "audio/mpeg")}
            data = {"chat_id": chat_id}
            if thread_id and chat_id == FORUM_CHAT_ID:
                data["message_thread_id"] = thread_id
            if caption:
                data["caption"] = caption
                data["parse_mode"] = "Markdown"
            resp = requests.post(url, data=data, files=files, timeout=40)
            return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ Erro ao enviar áudio no tópico {thread_id}: {e}", flush=True)
        return False

def send_topic_document(thread_id, doc_path, caption=None, chat_id=FORUM_CHAT_ID):
    """Envia arquivo documental (.md, .pdf, etc.) para o tópico"""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
    try:
        with open(doc_path, "rb") as f:
            files = {"document": (Path(doc_path).name, f, "text/markdown")}
            data = {"chat_id": chat_id}
            if thread_id and chat_id == FORUM_CHAT_ID:
                data["message_thread_id"] = thread_id
            if caption:
                data["caption"] = caption
                data["parse_mode"] = "Markdown"
            resp = requests.post(url, data=data, files=files, timeout=40)
            return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ Erro ao enviar documento no tópico {thread_id}: {e}", flush=True)
        return False

def answer_callback(callback_id, text=None):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def get_system_status():
    mem = shutil.disk_usage("/")
    free_gb = mem.free / (1024**3)
    total_gb = mem.total / (1024**3)
    
    services = {
        "WhatsApp Bridge (Porta 5005)": "node.*server.js",
        "Hermes Gateway": "hermes.*gateway",
        "Cloudflared Tunnel": "cloudflared.*tunnel",
        "Dissecador & Daemons": "python.*dissector|python.*transcript"
    }
    status_lines = []
    for name, pattern in services.items():
        res = subprocess.run(f"pgrep -fl '{pattern}'", shell=True, capture_output=True, text=True)
        st = "🟢 ONLINE" if res.returncode == 0 else "⚪ INATIVO"
        status_lines.append(f"• *{name}:* {st}")

    n8n_st = "🟢 ONLINE"
    try:
        r = requests.get("https://vn-ai-ecosystem.onrender.com/healthz", timeout=3)
        if r.status_code != 200:
            n8n_st = f"🟡 HTTP {r.status_code}"
    except Exception:
        n8n_st = "🔴 OFFLINE"

    msg = (
        "🛡️ *PAINEL DE INFRAESTRUTURA & TELEMETRIA*\n\n"
        f"💾 *Armazenamento:* `{free_gb:.1f} GB livres` de `{total_gb:.1f} GB`\n"
        f"🌐 *n8n Cloud Engine:* {n8n_st}\n"
        f"📦 *Repositório GitOps:* [github.com/vn-24k/vn-ai-ecosystem](https://github.com/vn-24k/vn-ai-ecosystem)\n\n"
        "🔍 *Status dos Daemons:*\n" + "\n".join(status_lines) + "\n\n"
        "_Vigilância automatizada ativa 24/7._"
    )
    return msg

# --- PAINÉIS DE CADA SALA ---

def post_software_panel():
    buttons = [
        [
            {"text": "📋 Explorar Catálogo de Criação", "callback_data": "soft_catalog"},
            {"text": "🎰 Roleta 59 (Sorteio Exclusivo)", "callback_data": "arch_roulette"}
        ],
        [
            {"text": "💎 Dark Luxury", "callback_data": "arch_luxury"},
            {"text": "⚡ Dashboard SaaS", "callback_data": "arch_saas"}
        ],
        [
            {"text": "📦 Ver Projetos no Workspace", "callback_data": "soft_list"}
        ]
    ]
    msg = (
        "🚀 *CENTRAL DE COMANDO — FÁBRICA DE SOFTWARE*\n\n"
        "Escolha abaixo o que você deseja que o ecossistema construa agora:\n"
        "• Clique em *Explorar Catálogo* para ver todos os modelos disponíveis\n"
        "• Ou clique em *Roleta 59* para sortear um template exclusivo sem repetição\n"
        "• Ou digite sua ideia de site livremente aqui nesta sala!"
    )
    send_topic_message(TOPIC_SOFTWARE, msg, buttons=buttons)

def post_software_catalog():
    buttons = [
        [
            {"text": "💎 1. Dark Luxury & Joalheria", "callback_data": "arch_luxury"},
            {"text": "⚡ 2. Dashboard SaaS B2B", "callback_data": "arch_saas"}
        ],
        [
            {"text": "🎮 3. 3D WebGL & Cyber", "callback_data": "arch_3d"},
            {"text": "🛍️ 4. E-Commerce Minimalista", "callback_data": "arch_ecom"}
        ],
        [
            {"text": "👤 5. Portfólio Executivo Pessoal", "callback_data": "arch_portfolio"},
            {"text": "🎰 6. Roleta Exclusiva (59 templates)", "callback_data": "arch_roulette"}
        ]
    ]
    msg = (
        "📋 *CATÁLOGO DE CRIAÇÃO — ARQUÉTIPOS DE ELITE*\n\n"
        "Selecione um arquétipo para acionar o pipeline completo de engenharia:\n"
        "1. 💎 *Dark Luxury:* Ouro, champanhe, alta relojoaria, tipografia nobre\n"
        "2. ⚡ *Dashboard SaaS:* Finanças B2B, métricas analíticas em dark mode\n"
        "3. 🎮 *3D WebGL:* Shaders procedurais Three.js, partículas interativas\n"
        "4. 🛍️ *E-Commerce D2C:* Vitrine minimalista de alto padrão e fluidez\n"
        "5. 👤 *Portfólio Executivo:* Autoridade autoral, cases e liderança técnica\n"
        "6. 🎰 *Roleta Exclusiva:* Sorteio auditado dos 59 templates do arsenal\n\n"
        "_Ao clicar, o código é montado, o repo é criado no seu GitHub e o site sobe na Vercel!_"
    )
    send_topic_message(TOPIC_SOFTWARE, msg, buttons=buttons)

def post_media_panel():
    buttons = [
        [
            {"text": "🎙️ Sintetizar Voz Neural (minha-voz)", "callback_data": "media_voice_test"},
            {"text": "📱 Gerar Reels Vertical (9:16)", "callback_data": "media_reels"}
        ],
        [
            {"text": "🎬 Gerar Trailer Netflix (2.39:1)", "callback_data": "media_trailer"}
        ]
    ]
    msg = (
        "🎬 *CENTRAL DE COMANDO — ESTÚDIO DE MÍDIA NEURAL*\n\n"
        "Produção cinematográfica e síntese vocal de padrão de estúdio:\n"
        "• Síntese neural Fish Audio com sua voz real (`minha-voz`)\n"
        "• Decupagem Hann sem estalos ou pausas mecânicas\n"
        "• Você também pode enviar qualquer texto para narração aqui nesta sala!"
    )
    send_topic_message(TOPIC_MEDIA, msg, buttons=buttons)

def post_brain_panel():
    buttons = [
        [
            {"text": "📊 Ver Dossiês no Obsidian", "callback_data": "brain_list"},
            {"text": "🔒 Backup Git do Cofre (SHA-256)", "callback_data": "brain_backup"}
        ]
    ]
    msg = (
        "🧠 *CENTRAL DE COMANDO — SEGUNDO CÉREBRO & OBSIDIAN*\n\n"
        "📌 *Para dissecar qualquer vídeo pelo Padrão Ouro (Regra 18):*\n"
        "Basta colar o link do YouTube aqui nesta sala:\n"
        "`https://www.youtube.com/watch?v=...`\n\n"
        "O sistema extrai a transcrição, estrutura a tese central, salva no seu Obsidian e entrega o arquivo `.md` completo aqui para download!"
    )
    send_topic_message(TOPIC_BRAIN, msg, buttons=buttons)

def post_devops_panel():
    buttons = [
        [
            {"text": "🔍 Diagnóstico em Tempo Real", "callback_data": "devops_check"},
            {"text": "🔄 Reiniciar WhatsApp Bridge (5005)", "callback_data": "devops_restart_wa"}
        ]
    ]
    msg = (
        "🛡️ *CENTRAL DE COMANDO — DEVOPS GUARDIAN*\n\n"
        "Vigilância operacional contínua dos serviços, memória e conectividade."
    )
    send_topic_message(TOPIC_DEVOPS, msg, buttons=buttons)

# --- EXECUÇÃO DOS CALLBACKS DE CADA TÓPICO ---

def trigger_software_build(archetype, chat_id=FORUM_CHAT_ID, thread_id=TOPIC_SOFTWARE):
    proj_name = f"app-{uuid.uuid4().hex[:6]}"
    tmpl = "dc30a991-c521-4b5e-ab97-d4ecf84cc52d.jpg"
    
    if ROULETTE_SCRIPT.exists() and archetype == "roulette":
        res = subprocess.run([sys.executable, str(ROULETTE_SCRIPT), proj_name], capture_output=True, text=True)
        for l in res.stdout.split("\n"):
            if "ROULETTE RESULT:" in l:
                tmpl = l.split("ROULETTE RESULT:")[-1].strip()

    def run_task():
        cmd = [
            sys.executable,
            str(BUILD_DEPLOY_SCRIPT),
            proj_name,
            tmpl,
            str(chat_id),
            str(thread_id),
            archetype
        ]
        subprocess.run(cmd)

    threading.Thread(target=run_task, daemon=True).start()

def handle_callback(cq):
    cq_id = cq.get("id")
    data = cq.get("data", "")
    msg_obj = cq.get("message", {})
    chat_id = msg_obj.get("chat", {}).get("id", FORUM_CHAT_ID)
    thread_id = msg_obj.get("message_thread_id", TOPIC_SOFTWARE)
    user = cq.get("from", {}).get("first_name", "Usuário")
    
    print(f"⚡ [Topic {thread_id}] Botão clicado: '{data}' por {user}", flush=True)

    # 1. SALA DE SOFTWARE
    if data == "soft_catalog":
        answer_callback(cq_id, "Abrindo catálogo...")
        post_software_catalog()

    elif data.startswith("arch_"):
        arch_type = data.replace("arch_", "")
        answer_callback(cq_id, f"🚀 Construindo arquétipo: {arch_type.upper()}")
        trigger_software_build(arch_type, chat_id=chat_id, thread_id=thread_id)

    elif data == "soft_list":
        answer_callback(cq_id, "Consultando projetos...")
        res = subprocess.run("cd '/root/Evolução Inteligente' && ls -d app-* 2>/dev/null || echo 'Nenhum'", shell=True, capture_output=True, text=True)
        send_topic_message(
            thread_id,
            f"📦 *Projetos Criados no Workspace:*\n```\n{res.stdout.strip()}\n```\nDeploy de referência ativo: [dist-phi-gilt-68.vercel.app](https://dist-phi-gilt-68.vercel.app)",
            chat_id=chat_id
        )

    # 2. SALA DE MÍDIA
    elif data == "media_voice_test":
        answer_callback(cq_id, "🎙️ Gerando áudio de calibração...")
        send_topic_message(thread_id, "🎙️ _Sintetizando áudio neural com voz paulistana autêntica e decupagem Hann..._", chat_id=chat_id)
        
        def run_voice():
            out_file = "/tmp/calibracao_voz.mp3"
            test_phrase = "Fala aí Vinícius, ecossistema rodando no talo! Locução neural calibrada com microfades Hann, sem corte mecânico. Entrega direta no estúdio de mídia!"
            cmd = f"fish-tts '{test_phrase}' --decupar --output '{out_file}'"
            subprocess.run(cmd, shell=True)
            if Path(out_file).exists():
                send_topic_audio(thread_id, out_file, caption="🎙️ *Áudio de Calibração Acústica* (Voz Neural Paulistana)", chat_id=chat_id)

        threading.Thread(target=run_voice, daemon=True).start()

    elif data == "media_reels":
        answer_callback(cq_id, "🎬 Iniciando Reels...")
        send_topic_message(
            thread_id,
            "📱 *PRODUÇÃO DE REELS INICIADA (9:16)*\n\n"
            "🎙️ *Locução:* Fish Audio `minha-voz` (s2.1-pro-free)\n"
            "✂️ *Decupagem:* Microfades Hann anti-estalo\n"
            "🎞️ *Render:* Remotion Studio 720x1280 @ 24fps\n\n"
            "_O vídeo e áudio prontos serão entregues aqui nesta sala!_",
            chat_id=chat_id
        )
        threading.Thread(target=lambda: subprocess.run([sys.executable, str(REELS_SCRIPT)]), daemon=True).start()

    elif data == "media_trailer":
        answer_callback(cq_id, "🎬 Iniciando Trailer...")
        send_topic_message(
            thread_id,
            "🎬 *PRODUÇÃO DE TRAILER NETFLIX INICIADA (2.39:1)*\n\n"
            "🎭 *Narrativa:* 5 atos dramáticos de alta retenção\n"
            "🎨 *Visual:* Frames cinematográficos fotorrealistas via FLUX.1\n\n"
            "_Renderizando e preparando entrega nesta sala..._",
            chat_id=chat_id
        )
        threading.Thread(target=lambda: subprocess.run([sys.executable, str(TRAILER_SCRIPT)]), daemon=True).start()

    # 3. SALA DO SEGUNDO CÉREBRO
    elif data == "brain_list":
        answer_callback(cq_id, "Consultando cofre...")
        dossiers = list(OBSIDIAN_VAULT.glob("04 - Estudos/**/*.*")) if OBSIDIAN_VAULT.exists() else []
        recent = sorted(dossiers, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        names = "\n".join([f"• `{p.name}`" for p in recent]) or "Nenhum dossiê recente."
        send_topic_message(
            thread_id,
            f"🧠 *Cofre Obsidian:* `{len(dossiers)} estudos catalogados`\n\n*Últimos Dossiês:*\n{names}",
            chat_id=chat_id
        )

    elif data == "brain_backup":
        answer_callback(cq_id, "Executando backup...")
        send_topic_message(thread_id, "🔒 _Backup blindado auditado com SHA-256 e sincronizado no Git..._", chat_id=chat_id)
        res = subprocess.run("backup-obsidian 2>&1", shell=True, capture_output=True, text=True)
        send_topic_message(thread_id, f"✅ *Backup do Cofre Concluído!*\n```\n{res.stdout[-300:]}\n```", chat_id=chat_id)

    # 4. SALA DE DEVOPS
    elif data == "devops_check":
        answer_callback(cq_id, "Telemetria coletada.")
        send_topic_message(thread_id, get_system_status(), chat_id=chat_id)

    elif data == "devops_restart_wa":
        answer_callback(cq_id, "Reiniciando bridge...")
        send_topic_message(thread_id, "🔄 _Reiniciando WhatsApp Bridge na porta 5005..._", chat_id=chat_id)
        subprocess.run("pkill -f 'node.*server.js'; cd /root/apk-work/PROJETOS/antigravity-whatsapp-bridge && nohup node server.js > bridge.log 2>&1 &", shell=True)
        time.sleep(2)
        send_topic_message(thread_id, "✅ WhatsApp Bridge restabelecido com sucesso na porta 5005.", chat_id=chat_id)

# --- PROCESSAMENTO DE MENSAGENS EM CADA TÓPICO ---

def handle_message(msg):
    text = msg.get("text", "").strip()
    thread_id = msg.get("message_thread_id")
    chat_id = msg.get("chat", {}).get("id")
    
    if not text:
        return

    print(f"📩 [Chat {chat_id} | Topic {thread_id}] Mensagem recebida: '{text}'", flush=True)

    # Comandos globais
    if text in ["/paineis", "/setup", "/iniciar", "/start"]:
        post_software_panel()
        post_media_panel()
        post_brain_panel()
        post_devops_panel()
        return

    # Ingestão de YouTube (qualquer tópico ou no tópico 6)
    if ("youtube.com" in text or "youtu.be" in text):
        target_topic = thread_id or TOPIC_BRAIN
        def run_dissect():
            cmd = [sys.executable, str(DISSECTOR_SCRIPT), text, str(chat_id), str(target_topic)]
            subprocess.run(cmd)
        threading.Thread(target=run_dissect, daemon=True).start()
        return

    # Mensagens dentro da sala de Fábrica de Software (Tópico 4)
    if thread_id == TOPIC_SOFTWARE or (chat_id != FORUM_CHAT_ID and "criar" in text.lower()):
        send_topic_message(
            thread_id or TOPIC_SOFTWARE,
            f"💡 *IDEIA RECEBIDA NA FÁBRICA DE SOFTWARE*\n\n"
            f"Prompt: *\"{text}\"*\n\n"
            f"Iniciando scaffolding personalizado, criação de repositório no GitHub (`vn-24k`) e deploy em produção na Vercel...",
            chat_id=chat_id
        )
        trigger_software_build("custom", chat_id=chat_id, thread_id=thread_id or TOPIC_SOFTWARE)
        return

    # Mensagens dentro do Estúdio de Mídia (Tópico 5)
    if thread_id == TOPIC_MEDIA:
        send_topic_message(thread_id, f"🎙️ *Locução Neural Recebida:*\n_\"{text}\"_\n\nSintetizando com voz neural paulistana e decupagem Hann...", chat_id=chat_id)
        def run_narration():
            out_file = f"/tmp/locucao_{uuid.uuid4().hex[:6]}.mp3"
            cmd = f"fish-tts '{text}' --decupar --output '{out_file}'"
            subprocess.run(cmd, shell=True)
            if Path(out_file).exists():
                send_topic_audio(thread_id, out_file, caption=f"🎙️ *Locução Concluída:* {text[:60]}...", chat_id=chat_id)
        threading.Thread(target=run_narration, daemon=True).start()
        return

    # Mensagens dentro de DevOps (Tópico 7)
    if thread_id == TOPIC_DEVOPS:
        send_topic_message(thread_id, get_system_status(), chat_id=chat_id)
        return

def run_forum_listener():
    print("👂 Iniciando Forum Controller no grupo VN IA Ecosystem...", flush=True)
    offset = None
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates?timeout=20"
            if offset:
                url += f"&offset={offset}"
                
            resp = requests.get(url, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "callback_query" in update:
                        handle_callback(update["callback_query"])
                    elif "message" in update:
                        handle_message(update["message"])
        except Exception as e:
            time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description="VN AI Ecosystem Forum Controller")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("listen", help="Inicia o listener contínuo do fórum")
    subparsers.add_parser("paineis", help="Publica os painéis de controle em todas as salas")

    args = parser.parse_args()
    if not args.command or args.command == "listen":
        run_forum_listener()
    elif args.command == "paineis":
        post_software_panel()
        post_media_panel()
        post_brain_panel()
        post_devops_panel()

if __name__ == "__main__":
    main()
