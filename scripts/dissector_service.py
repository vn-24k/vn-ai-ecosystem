#!/usr/bin/env python3
"""
VN AI ECOSYSTEM — Autonomous YouTube Dissector & Second Brain Synchronizer
Segue o Padrão Ouro (Regra 18):
- Extrai transcrição e metadados
- Disseca Tese Central, Pilares, Insights e Aplicação Prática
- Grava no cofre Obsidian (/sdcard/Documents/Obsidian VN/VN/04 - Estudos)
- Faz commit Git
- Envia o arquivo .md diretamente para o tópico de Segundo Cérebro no Telegram Fórum
"""

import os
import sys
import json
import re
import time
import subprocess
from pathlib import Path
import urllib.request
import requests
from youtube_transcript_api import YouTubeTranscriptApi

DEFAULT_FORUM_CHAT_ID = -1004493467706
DEFAULT_TOPIC_BRAIN = 6

CONFIG_FILE = Path("/root/.config/integrations.json")

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

cfg = load_config()
TG_TOKEN = cfg.get("telegram", {}).get("bot_token", "")
OPENROUTER_KEY = cfg.get("openrouter", {}).get("api_key", os.environ.get("OPENROUTER_API_KEY", ""))
OBSIDIAN_VAULT = Path("/sdcard/Documents/Obsidian VN/VN")
STUDIES_DIR = OBSIDIAN_VAULT / "04 - Estudos"

def sanitize_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', '', name)
    return clean[:80].strip()

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
        requests.post(url, json=payload, timeout=12)
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}", flush=True)

def send_topic_document(chat_id, thread_id, file_path, caption=None):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": (file_path.name, f, "text/markdown")}
            data = {
                "chat_id": chat_id,
                "message_thread_id": thread_id,
            }
            if caption:
                data["caption"] = caption
                data["parse_mode"] = "Markdown"
            resp = requests.post(url, data=data, files=files, timeout=40)
            return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ Erro ao enviar documento: {e}", flush=True)
        return False

def extract_video_id(url):
    m = re.search(r'(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else url.strip()

def get_video_info(url):
    try:
        res = subprocess.run(
            ["yt-dlp", "--dump-json", "--skip-download", "--no-warnings", url],
            capture_output=True,
            text=True,
            timeout=20
        )
        if res.returncode == 0 and res.stdout:
            data = json.loads(res.stdout)
            return {
                "title": data.get("title", "Estudo de Vídeo"),
                "channel": data.get("uploader", "YouTube"),
                "views": data.get("view_count", 0),
                "duration": data.get("duration", 0),
                "url": url
            }
    except Exception as e:
        print(f"⚠️ Erro ao coletar metadados com yt-dlp: {e}", flush=True)
        
    vid = extract_video_id(url)
    return {
        "title": f"Estudo do Vídeo {vid}",
        "channel": "YouTube",
        "views": 0,
        "duration": 0,
        "url": url
    }

def get_transcript(vid):
    try:
        ytt = YouTubeTranscriptApi()
        tl = ytt.list(vid)
        try:
            t = tl.find_transcript(['pt-BR', 'pt', 'pt-PT', 'en', 'es'])
        except Exception:
            t = next(iter(tl))
        snippets = t.fetch()
        full_text = " ".join([getattr(s, "text", "") for s in snippets])
        return snippets, full_text
    except Exception as e:
        print(f"⚠️ Erro na extração da transcrição: {e}", flush=True)
        return [], ""

def analyze_with_ai(title, channel, text):
    prompt = f"""Você é um analista sênior de inteligência e cognição humana. Dissect o conteúdo a seguir extraído do canal '{channel}' com título '{title}'.
Gere uma análise densa, cirúrgica e livre de enrolação ou jargões vazios, seguindo estritamente estas seções em Markdown:

### 🎯 Tese Central
Qual é o argumento definitivo ou mensagem central do autor? (1 a 2 parágrafos incisivos)

### 🏛️ Pilares Fundamentais
Os 3 a 5 conceitos basilares que sustentam o raciocínio.

### 💡 Insights & Quebras de Paradigma
Pontos contra-intuitivos, viradas de chave e erros comuns cometidos pela maioria.

### 🛡️ Aplicação Prática & Soberania
Como aplicar este conhecimento de forma imediata na rotina, foco, negócios e blindagem psicológica (baseado na TCC e ação real).

Texto do vídeo:
{text[:9000]}
"""
    try:
        r = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={'Authorization': f'Bearer {OPENROUTER_KEY}', 'Content-Type': 'application/json'},
            json={
                'model': 'google/gemini-2.5-flash',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 2000,
                'temperature': 0.4
            },
            timeout=40
        )
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            print(f"⚠️ Erro OpenRouter: {r.status_code} - {r.text[:120]}", flush=True)
    except Exception as e:
        print(f"⚠️ Erro na IA: {e}", flush=True)
    return "Análise sintética em processamento."

def dissect_video(url, chat_id=DEFAULT_FORUM_CHAT_ID, thread_id=DEFAULT_TOPIC_BRAIN):
    print(f"🧠 Iniciando dissecação para: {url} no tópico {thread_id}...", flush=True)
    
    send_topic_message(
        chat_id,
        thread_id,
        f"🧠 *DISSECADOR DO SEGUNDO CÉREBRO ATIVADO*\n\n"
        f"🔗 *URL:* `{url}`\n"
        f"⏳ _Extraindo transcrição, identificando teses centrais e formatando o Dossiê Mestre..._"
    )
    
    vid = extract_video_id(url)
    info = get_video_info(url)
    snippets, full_text = get_transcript(vid)
    
    if not full_text:
        send_topic_message(
            chat_id,
            thread_id,
            f"⚠️ *Não foi possível extrair a transcrição automática deste vídeo.*\n"
            f"Verifique se o vídeo possui legendas ativas ou se é restrito."
        )
        return
        
    analysis = analyze_with_ai(info["title"], info["channel"], full_text)
    
    # Criar nota Markdown
    channel_clean = sanitize_filename(info["channel"])
    title_clean = sanitize_filename(info["title"])
    dest_dir = STUDIES_DIR / channel_clean
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_file = dest_dir / f"{title_clean}.md"
    today = time.strftime("%Y-%m-%d")
    
    md_content = f"""---
aliases: ["{info['title']}"]
tags:
  - segundo-cerebro
  - estudo
  - dissecação
  - {channel_clean.lower().replace(' ', '-')}
canal: "{info['channel']}"
url: "{info['url']}"
data: "{today}"
status: "concluído"
---

# 🧠 Dossiê Mestre: {info['title']}

**Canal:** [[{info['channel']}]]  
**Fonte Original:** [Assistir no YouTube]({info['url']})  
**Data da Dissecação:** {today}  

---

## ⚡ Síntese Estruturada & Insights

{analysis}

---

## 📜 Transcrição Integral Organizada

{full_text}

---
*Dossiê gerado e sincronizado pelo VN AI Ecosystem no Segundo Cérebro do Obsidian.*
"""
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"✅ Dossiê salvo em: {dest_file}", flush=True)
    
    # Git commit no cofre
    try:
        subprocess.run("git add . && git commit -m 'feat: estudo dissecado " + title_clean[:30] + "'", shell=True, cwd=str(OBSIDIAN_VAULT), capture_output=True)
    except Exception:
        pass
        
    # Enviar documento .md para o Telegram Topic
    caption = (
        f"✅ *DOSSIÊ MESTRE SALVO NO OBSIDIAN!*\n\n"
        f"📚 *Canal:* `{info['channel']}`\n"
        f"🎬 *Título:* {info['title']}\n"
        f"📁 *Local:* `04 - Estudos/{channel_clean}/{dest_file.name}`\n\n"
        f"Baixe o arquivo `.md` completo abaixo ou acesse no seu cofre Obsidian:"
    )
    send_topic_document(chat_id, thread_id, dest_file, caption=caption)
    print("🚀 Documento entregue no tópico do Telegram com sucesso!", flush=True)

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else ""
    c_id = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_FORUM_CHAT_ID
    th_id = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_TOPIC_BRAIN
    if target_url:
        dissect_video(target_url, c_id, th_id)
    else:
        print("Uso: dissector_service.py <URL> [CHAT_ID] [THREAD_ID]")
