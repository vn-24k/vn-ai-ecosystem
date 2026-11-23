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

def send_telegram(text, reply_markup=None, bot_type="default"):
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

def cmd_status(args=None):
    """Gera diagnóstico forense do ecossistema"""
    print("\n" + "="*60)
    print("🏛️  VN AI ECOSYSTEM — DIAGNÓSTICO DO ESTADO OPERACIONAL")
    print("="*60)
    
    # Memória e Disco
    mem = shutil.disk_usage("/")
    free_gb = mem.free / (1024**3)
    total_gb = mem.total / (1024**3)
    print(f"💾 Armazenamento Local: {free_gb:.1f} GB livres de {total_gb:.1f} GB ({mem.used/mem.total*100:.1f}% em uso)")
    
    # Processos Críticos
    print("\n🔍 Vigilância de Serviços:")
    services = {
        "WhatsApp Bridge (Porta 5005)": "node.*server.js",
        "Hermes Gateway": "hermes.*gateway",
        "Cloudflared Tunnel": "cloudflared.*tunnel",
        "Dissecador Daemon": "transcript-daemon"
    }
    for name, pattern in services.items():
        res = subprocess.run(f"pgrep -fl '{pattern}'", shell=True, capture_output=True, text=True)
        status = "🟢 ONLINE" if res.returncode == 0 else "⚪ INATIVO"
        print(f"  • {name}: {status}")

    # Repositório GitOps
    print("\n📦 GitOps Core (GitHub):")
    res = subprocess.run("cd /root/vn-ai-ecosystem && git status -s && git rev-parse --short HEAD", 
                         shell=True, capture_output=True, text=True)
    commit = res.stdout.strip().split("\n")[-1] if res.returncode == 0 else "Desconhecido"
    print(f"  • Repositório: https://github.com/vn-24k/vn-ai-ecosystem")
    print(f"  • Último Commit: {commit} (branch main sincronizada)")

    # Segundo Cérebro (Obsidian)
    print("\n🧠 Segundo Cérebro (Obsidian):")
    if OBSIDIAN_VAULT.exists():
        dossiers = list(OBSIDIAN_VAULT.glob("04 - Estudos/**/*.*"))
        projects = list(OBSIDIAN_VAULT.glob("01 - Projetos/**/*.*"))
        print(f"  • Cofre Localizado: {OBSIDIAN_VAULT}")
        print(f"  • Projetos Ativos: {len(projects)} notas")
        print(f"  • Dossiês de Estudos: {len(dossiers)} arquivos de inteligência")
    else:
        print("  ⚠️ Cofre não localizado no caminho padrão.")
    print("="*60 + "\n")

def cmd_spin(args):
    """Executa a roleta anti-repetição de 59 templates"""
    project_name = args.project or f"project-{uuid.uuid4().hex[:6]}"
    print(f"🎰 Acionando Roleta Persistente para o projeto: '{project_name}'...")
    if ROULETTE_SCRIPT.exists():
        res = subprocess.run([sys.executable, str(ROULETTE_SCRIPT), project_name], capture_output=True, text=True)
        print(res.stdout)
        if res.stderr:
            print(res.stderr)
    else:
        print("❌ Script spin_roulette.py não encontrado no arsenal.")

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
    else:
        print(f"❌ Tipo de mídia desconhecido: '{tipo}'. Escolha 'reels' ou 'trailer'.")

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

def main():
    parser = argparse.ArgumentParser(description="VN AI Ecosystem — Central Dispatcher")
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Exibe o status completo do ecossistema")

    # spin
    p_spin = subparsers.add_parser("spin", help="Sorteia template de design via roleta persistente")
    p_spin.add_argument("project", nargs="?", default="", help="Nome do projeto")

    # media
    p_media = subparsers.add_parser("media", help="Aciona estúdio cinematográfico de mídia")
    p_media.add_argument("type", choices=["reels", "trailer"], help="Tipo de mídia a gerar")

    # menu
    subparsers.add_parser("menu", help="Envia o menu interativo no Telegram")

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

if __name__ == "__main__":
    main()
