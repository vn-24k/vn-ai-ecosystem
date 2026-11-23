#!/usr/bin/env python3
"""
VN AI ECOSYSTEM — Automated Workflow Importer & Synchronizer
Imports all modular workflows into the remote n8n instance via public API.
"""

import os
import sys
import glob
import json
import urllib.request
import urllib.error

CONFIG_FILE = "/root/.config/integrations.json"

def get_n8n_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg.get("n8n", {})

def import_all():
    n8n_cfg = get_n8n_config()
    base_url = n8n_cfg.get("base_url", "https://vn-ai-ecosystem.onrender.com").rstrip("/")
    api_key = n8n_cfg.get("api_key", "")
    
    if not api_key:
        print("❌ Erro: n8n api_key não configurada em integrations.json")
        sys.exit(1)
        
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    workflow_files = sorted(glob.glob("/root/vn-ai-ecosystem/workflows/*.json"))
    print(f"📦 Localizados {len(workflow_files)} workflows para importar no n8n ({base_url})...\n")

    for wf_path in workflow_files:
        with open(wf_path, "r", encoding="utf-8") as f:
            wf_data = json.load(f)
            
        name = wf_data.get("name")
        payload = {
            "name": name,
            "nodes": wf_data.get("nodes", []),
            "connections": wf_data.get("connections", {}),
            "settings": wf_data.get("settings", {"executionOrder": "v1"})
        }

        req = urllib.request.Request(
            f"{base_url}/api/v1/workflows",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode())
                wf_id = res_data.get("id")
                print(f"✅ Importado com sucesso: [{wf_id}] \"{name}\"")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode()
            print(f"⚠️ Erro ao importar \"{name}\": HTTP {e.code} - {err_msg}")
        except Exception as e:
            print(f"❌ Falha inesperada em \"{name}\": {e}")

if __name__ == "__main__":
    import_all()
