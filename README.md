# ShopMate

ShopMate is an AI-powered shopping assistant with a FastAPI backend and a Next.js frontend. It supports product discovery, demo-mode recommendations, and optional Gemini-powered responses.

## Project structure

- `frontend/` - Next.js app
- `shopmate-bakend/` - FastAPI backend
- `Gen/` - experimental or legacy app files
- `projects/` - additional project files

## Features

- AI-style shopping assistant UI
- Product search and recommendation flow
- Demo catalog mode when no Gemini key is configured
- FastAPI API for chat and image-based product lookups

## Run locally

### Backend

```bash
cd shopmate-bakend
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn python-dotenv google-generativeai
python main.py
```

The backend runs on `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:3000`.

## GitHub deployment

Create a repository on GitHub, then run:

```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

## Notes

- Add your Gemini API key in `shopmate-bakend/api.env` as `GEMINI_API_KEY=...` for AI mode.
- If no key is set, the app runs in demo mode.
