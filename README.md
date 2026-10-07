# AuraHealth AI (master pack)
- `docs/` live app for GitHub Pages (metrics, foods matrix, training, steps, progress and recovery, CNN + RAG food scan, 3-agent coach, memory assistant, offline PWA)
- `fullstack/` Docker stack (FastAPI, LangGraph, ChromaDB, Postgres, Redis, Node sync, Prometheus, Grafana). Run locally; see its README.

## Publish from Termux
```bash
pkg update -y && pkg install -y git unzip curl
termux-setup-storage                      # allow storage access
cp ~/storage/downloads/aurahealth-ai-master.zip ~ && cd ~ && unzip -o aurahealth-ai-master.zip && cd aurahealth-ai
git config --global user.name "Nikhil Chary Sriramoju"
git config --global user.email "YOUR_GITHUB_EMAIL"
git config --global credential.helper store
export TOKEN=ghp_xxx                      # classic token with "repo" scope
curl -s -X POST -H "Authorization: Bearer $TOKEN" https://api.github.com/user/repos -d '{"name":"aurahealth-ai","private":false}' | head -3
git init -b main && git add . && git commit -m "AuraHealth AI"
git remote add origin https://github.com/Nikhil-creat/aurahealth-ai.git
git push -u origin main                   # username Nikhil-creat, password = the token
curl -s -X POST -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/Nikhil-creat/aurahealth-ai/pages -d '{"source":{"branch":"main","path":"/docs"}}' | head -3
```
Open https://nikhil-creat.github.io/aurahealth-ai/ in 1-2 minutes. Update later with `git add . && git commit -m "update" && git push`.
Then open the app, go to Settings and paste a free Groq key to switch on the LLM agents and assistant.
