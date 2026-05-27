# Backend Product Requirements Document (PRD)

Backend specifications for **AlbumAI Studio v2.0**.

---

## 🎯 Functional Requirements

### 1. Photo & Object Detection (DINO Core)
* **API Endpoint:** `POST /api/detect` and `POST /api/detect/batch`
* **Performance Metric:** Process a 600 DPI image (approx. 4000x3000px) in < 1.5s on a modern NVIDIA GPU or < 5s on CPU.
* **Accuracy Target:** F1-score of `0.94` on typical multi-photo photo prints.
* **Deduplication Check:** Run perceptual hash (pHash) on crop finish to identify close duplicates and prompt users on the gallery.

### 2. Live Color Revitalization (PRO)
* **API Endpoint:** `POST /api/retouch/revitalize` and `/api/retouch/manual`
* **Mechanisms:**
  * **Gray World White Balance:** Calculate color channel means and shift to neutral grey.
  * **Acid Paper Filter:** Specifically target and pull back orange-yellow casts typical of deteriorated backing papers.
  * **CLAHE:** Apply Adaptive Histogram Equalization with dynamic clip limits to prevent over-saturation.

### 3. Face Identification (ULTRA)
* **API Endpoint:** `POST /api/faces/cluster`
* **Mechanism:** Extract 512-dim face embeddings using InsightFace (`buffalo_l`). Cluster identities using HDBSCAN. Output a unique `face_cluster_id` saved directly into Supabase Postgres.

---

## ⚙️ Technical Constraints & Dependencies

* **Language:** Python 3.11+
* **Framework:** FastAPI with Uvicorn standard process.
* **Concurrency:** Celery with Redis backend for heavy async processing (Upscaling, batch indexing) to keep API endpoints non-blocking.
* **Error Toleration:** Graceful fallback to OpenCV/Pillow filters if deep learning models fail to load due to RAM limits.
* **Rate Limits:** Enforce maximum of 10 requests per minute for unauthenticated users using `slowapi`.

---

## 📈 Success Metrics (KPIs)
* API Uptime: `99.9%`
* Average Crop Time: `< 2.5s` per standard scan sheet.
* CPU/RAM ceiling: Max `4GB` memory usage during concurrent CPU processing.
