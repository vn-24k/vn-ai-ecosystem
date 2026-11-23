#!/usr/bin/env python3
"""
VN AI ECOSYSTEM — Enterprise Dispatcher & Command Daemon
Unifica os 6 motores do ecossistema (Software, Cinema/Áudio, Dissecador, Cyber Lab, Multi-Agent e Sentinel)
com interface CLI executiva e conexão direta com o Telegram.
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
REELS_SCRIPT = Path("/root/scripts/gerar_reels_masterpiece.py")
TRAILER_SCRIPT = Path("/root/scripts/gerar_trailer_netflix.py")

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def send_telegram(text, reply_markup=None):
    cfg = load_config()
    tg_cfg = cfg.get("telegram", {})
    token = tg_cfg.get("bot_token", "REDACTED_TELEGRAM_TOKEN")
    chat_id = tg_cfg.get("chat_id", "2140439370")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")
        return False

def answer_callback(callback_id, text=None):
    cfg = load_config()
    tg_cfg = cfg.get("telegram", {})
    token = tg_cfg.get("bot_token", "REDACTED_TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def get_system_status_text():
    mem = shutil.disk_usage("/")
    free_gb = mem.free / (1024**3)
    total_gb = mem.total / (1024**3)
    
    services = {
        "WhatsApp Bridge (Porta 5005)": "node.*server.js",
        "Hermes Gateway": "hermes.*gateway",
        "Cloudflared Tunnel": "cloudflared.*tunnel",
        "Dissecador Daemon": "transcript-daemon"
    }
    status_lines = []
    for name, pattern in services.items():
        res = subprocess.run(f"pgrep -fl '{pattern}'", shell=True, capture_output=True, text=True)
        st = "🟢 ONLINE" if res.returncode == 0 else "⚪ INATIVO"
        status_lines.append(f"• *{name}:* {st}")

    n8n_st = "🟢 ONLINE (HTTP 200)"
    try:
        r = requests.get("https://vn-ai-ecosystem.onrender.com/healthz", timeout=3)
        if r.status_code != 200:
            n8n_st = f"🟡 HTTP {r.status_code}"
    except Exception:
        n8n_st = "🔴 OFFLINE"

    msg = (
        "🏛️ *VN AI ECOSYSTEM — STATUS OPERACIONAL*\n\n"
        f"💾 *Disco:* `{free_gb:.1f} GB livres` de `{total_gb:.1f} GB`\n"
        f"🌐 *n8n Cloud Engine:* {n8n_st}\n"
        f"📦 *Workflows Importados:* `6 Motores de Elite`\n\n"
        "🔍 *Vigilância de Serviços:*\n" + "\n".join(status_lines) + "\n\n"
        "🔗 *Painel Cloud:* [vn-ai-ecosystem.onrender.com](https://vn-ai-ecosystem.onrender.com)"
    )
    return msg

def cmd_status(args=None):
    """Gera diagnóstico forense do ecossistema"""
    print("\n" + "="*60)
    print("🏛️  VN AI ECOSYSTEM — DIAGNÓSTICO DO ESTADO OPERACIONAL")
    print("="*60)
    print(get_system_status_text())
    print("="*60 + "\n")

def execute_spin(project_name=None):
    project_name = project_name or f"proj-{uuid.uuid4().hex[:6]}"
    if ROULETTE_SCRIPT.exists():
        res = subprocess.run([sys.executable, str(ROULETTE_SCRIPT), project_name], capture_output=True, text=True)
        return res.stdout
    return "Script spin_roulette.py não localizado."

def cmd_spin(args):
    """Executa a roleta anti-repetição de 59 templates"""
    p_name = args.project if hasattr(args, 'project') and args.project else f"proj-{uuid.uuid4().hex[:6]}"
    print(f"🎰 Acionando Roleta Persistente para o projeto: '{p_name}'...")
    output = execute_spin(p_name)
    print(output)

def cmd_media(args):
    """Dispara a produção de mídia cinematográfica com Fish Audio e Remotion"""
    tipo = args.type.lower()
    print(f"🎬 Disparando Motor de Mídia ({tipo.upper()})...")
    
    if tipo == "reels":
        if REELS_SCRIPT.exists():
            print("🚀 Executando pipeline de Reels Vertical 9:16 com voz clonada e decupagem Hann...")
            subprocess.run([sys.executable, str(REELS_SCRIPT)])
        else:
            print("❌ Script gerar_reels_masterpiece.py não encontrado.")
    elif tipo == "trailer":
        if TRAILER_SCRIPT.exists():
            print("🚀 Executando pipeline de Trailer Cinematográfico 2.39:1...")
            subprocess.run([sys.executable, str(TRAILER_SCRIPT)])
        else:
            print("❌ Script gerar_trailer_netflix.py não encontrado.")

def cmd_menu_telegram(args=None):
    """Envia o menu executivo interativo no Telegram"""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🚀 Fábrica de Software", "callback_data": "cmd_software"},
                {"text": "🎬 Estúdio de Mídia (Reels)", "callback_data": "cmd_reels"}
            ],
            [
                {"text": "🧠 Dossiê Obsidian (Regra 18)", "callback_data": "cmd_dissecar"},
                {"text": "🛡️ Diagnóstico do Sistema", "callback_data": "cmd_status"}
            ]
        ]
    }
    msg = (
        "⚡ *VN AI ECOSYSTEM — CENTRAL DE COMANDO EXECUTIVO*\n\n"
        "Plataforma pessoal de engenharia e orquestração de elite ativa.\n"
        "Selecione uma ação rápida abaixo:"
    )
    if send_telegram(msg, reply_markup=keyboard):
        print("✅ Menu Executivo enviado com sucesso para o Telegram!")
    else:
        print("❌ Falha ao enviar menu no Telegram.")

def handle_callback_query(cq):
    cq_id = cq.get("id")
    data = cq.get("data", "")
    user = cq.get("from", {}).get("first_name", "Usuário")
    print(f"⚡ [Telegram Event] Botão clicado: '{data}' por {user}", flush=True)

    if data == "cmd_software":
        answer_callback(cq_id, "🎰 Acionando Fábrica de Software...")
        proj = f"app-{uuid.uuid4().hex[:6]}"
        result = execute_spin(proj)
        
        # Extrair nome do template
        template_name = "Desconhecido"
        for line in result.split("\n"):
            if "ROULETTE RESULT:" in line:
                template_name = line.split("ROULETTE RESULT:")[-1].strip()
                
        msg = (
            "🚀 *FÁBRICA DE SOFTWARE — LINHA DE MONTAGEM ATIVADA!*\n\n"
            f"📦 *Projeto:* `{proj}`\n"
            f"🎨 *Template Sorteado:* `{template_name}`\n"
            "🎰 *Mecanismo:* Roleta Persistente com registro anti-repetição (`ROULETTE_REGISTRY.json`)\n\n"
            "_Montando código real, criando repositório no GitHub e publicando na Vercel..._\n"
            "Os links do site ativo e do código serão entregues aqui em instantes!"
        )
        send_telegram(msg)
        
        # Disparar pipeline autônomo completo em segundo plano
        deploy_script = "/root/vn-ai-ecosystem/scripts/build_and_deploy.py"
        threading.Thread(
            target=lambda: subprocess.run([sys.executable, deploy_script, proj, template_name]),
            daemon=True
        ).start()

    elif data == "cmd_reels":
        answer_callback(cq_id, "🎬 Iniciando Pipeline de Reels...")
        msg = (
            "🎬 *ESTÚDIO DE MÍDIA — REELS VERTICAL 9:16*\n\n"
            "🎙️ *Voz:* Fish Audio `minha-voz` (s2.1-pro-free)\n"
            "✂️ *Decupagem:* Microfades Hann, eliminando pausas mortas >300ms\n"
            "📱 *Formato:* 720x1280 @ 24fps com legendas cinéticas\n\n"
            "_Iniciando renderização Remotion Studio em segundo plano..._"
        )
        send_telegram(msg)
        threading.Thread(target=lambda: subprocess.run([sys.executable, str(REELS_SCRIPT)]), daemon=True).start()

    elif data == "cmd_status":
        answer_callback(cq_id, "🛡️ Coletando telemetria...")
        status_report = get_system_status_text()
        send_telegram(status_report)

    elif data == "cmd_dissecar":
        answer_callback(cq_id, "🧠 Dissecador Cognitivo ativado!")
        msg = (
            "🧠 *DISSECADOR COGNITIVO — REGRA 18 ATIVA*\n\n"
            "Para dissecar um canal do YouTube com o Padrão Ouro:\n"
            "Envie o comando:\n"
            "`/dissecar https://www.youtube.com/@NomeDoCanal`\n\n"
            "• *Camada de Ouro:* Todos os vídeos com 100k+ visualizações\n"
            "• *Camada de Atualização:* 10 vídeos mais recentes\n"
            "• *Destino:* Dossiê Mestre no Obsidian com Dataview dinâmico."
        )
        send_telegram(msg)

    else:
        answer_callback(cq_id, "Comando recebido.")

def cmd_listen(args=None):
    """Daemon de escuta contínua de comandos e botões no Telegram"""
    cfg = load_config()
    tg_cfg = cfg.get("telegram", {})
    token = tg_cfg.get("bot_token", "REDACTED_TELEGRAM_TOKEN")
    
    print("👂 Iniciando Telegram Daemon Listener do VN AI Ecosystem...", flush=True)
    print("🤖 Bot conectado. Aguardando comandos e cliques nos botões...", flush=True)
    
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=20"
            if offset:
                url += f"&offset={offset}"
                
            resp = requests.get(url, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "callback_query" in update:
                        handle_callback_query(update["callback_query"])
                        
                    elif "message" in update:
                        msg = update["message"]
                        text = msg.get("text", "").strip()
                        user = msg.get("from", {}).get("first_name", "Usuário")
                        print(f"📩 [Telegram Message] '{text}' de {user}")
                        
                        if text in ["/start", "/menu", "/help"]:
                            cmd_menu_telegram()
                        elif text == "/status":
                            send_telegram(get_system_status_text())
                        elif text.startswith("/spin"):
                            parts = text.split(maxsplit=1)
                            proj = parts[1] if len(parts) > 1 else ""
                            res = execute_spin(proj)
                            send_telegram(f"🎰 *Roleta Executada:*\n```\n{res}\n```")
                            
        except Exception as e:
            time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description="VN AI Ecosystem — Central Dispatcher")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Exibe o status completo do ecossistema")
    
    p_spin = subparsers.add_parser("spin", help="Sorteia template via roleta persistente")
    p_spin.add_argument("project", nargs="?", default="", help="Nome do projeto")

    p_media = subparsers.add_parser("media", help="Aciona estúdio cinematográfico de mídia")
    p_media.add_argument("type", choices=["reels", "trailer"], help="Tipo de mídia")

    subparsers.add_parser("menu", help="Envia o menu interativo no Telegram")
    subparsers.add_parser("listen", help="Inicia o daemon ouvinte de comandos do Telegram")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        cmd_status(args)
    elif args.command == "spin":
        cmd_spin(args)
    elif args.command == "media":
        cmd_media(args)
    elif args.command == "menu":
        cmd_menu_telegram(args)
    elif args.command == "listen":
        cmd_listen(args)

if __name__ == "__main__":
    main()
