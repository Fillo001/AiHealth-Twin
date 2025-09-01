# AI Health Twin

AI Health Twin is a decentralized, AI-powered wellness companion that helps users monitor and improve their health while retaining ownership of their data.

## Features
- 🧠 AI insights based on health metrics
- 🔐 Web3 login with wallet (MetaMask, Phantom, etc.)
- 📊 Data visualization of wellness metrics
- 🌐 Decentralized storage (IPFS / Ceramic)
- 💰 Token rewards for sharing anonymized health data

## Quickstart

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
