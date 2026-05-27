# AlbumAI Studio v2.0 📷 ✨

> The ultimate production-grade scanned photo separator, enhancer, and organizer. Recalls the aesthetics of autocropper.io with the bulk workflow efficiency of AutoSplitter.

---

## 🎨 Overview & Ecosystem

AlbumAI Studio is a state-of-the-art monorepo combining a modern **Next.js 14** web editor with a highly optimized **FastAPI Python backend**. It enables users to extract individual photographs from large sheet scans automatically while restoring damaged vintage color tones.

```
albumai-studio/
├── frontend/             # Next.js 14 App Router, Tailwind, Konva Canvas
├── backend/              # FastAPI, Grounding DINO, Real-ESRGAN, InsightFace, CLIP
├── supabase/             # SQL schemas, RLS controls, storage buckets config
└── .github/              # Automation CI/CD lint, test, security pipelines
```

---

## 🧠 Core Features

* **AI Separation (CORE):** High-precision Grounding DINO zero-shot object detector splits overlapping photos instantly.
* **Color Revitalization (PRO):** Automates CLAHE contrast curves and gray-world white balance adjustments to pull back yellow casts on deteriorated acid paper.
* **Face & Event Indexing (ULTRA):** Groups identities using InsightFace and maps visual collections using OpenCLIP embeddings.
* **SaaS Tiers & Automation (SKILLS):** Automated workflow integration through n8n triggers and secure user billing scopes.

---

## 🚀 Quickstart Guide

### 1. Backend Server Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app/main.py
```

### 2. Frontend Interface Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Standalone Gradio Dashboard Run
```bash
cd backend
python standalone_app.py
```

---

## 🐳 Docker Deployment

To spin up the entire frontend, backend, Redis queue, and n8n nodes:
```bash
docker-compose up --build
```
* **Frontend UI:** `http://localhost:3000`
* **FastAPI Server:** `http://localhost:8000`
* **n8n dashboard:** `http://localhost:5678`
