# Full-Stack System Architecture: AlbumAI Studio v2.0

Comprehensive architectural mapping of the AlbumAI Studio ecosystem.

---

## 🏛️ C4 Container Diagram

```mermaid
graph TD
    User([User / Browser])
    
    subgraph Frontend [Next.js App Router - Port 3000]
        UI[React UI Components / Konva Canvas]
        Store[Zustand Store / State Management]
        Client[Supabase Client & Axios API Client]
    end
    
    subgraph Backend [FastAPI Server - Port 8000]
        API[FastAPI Router Endpoints]
        RouterAuth[Auth Router JWT / Supabase Auth]
        CoreML[AI Service Registry: DINO, CLIP, InsightFace]
        Enhance[Upscale / Retouch Processors]
    end
    
    subgraph Storage & Database [Supabase Cloud]
        DB[(Postgres SQL + pgvector)]
        AuthService[Supabase Auth Service]
        Buckets[Storage Buckets: scans, photos]
    end

    subgraph Automation [n8n Workflow Engine - Port 5678]
        n8nEngine[n8n Workflow Scheduler]
    end

    User -->|Interacts| UI
    UI -->|State Updates| Store
    UI -->|API Requests| Client
    
    Client -->|GraphQL / REST| DB
    Client -->|Signed URLs| Buckets
    Client -->|Custom REST API| API
    
    API -->|Authenticate| AuthService
    API -->|Process / Crop / Enhance| CoreML
    API -->|Write metadata| DB
    API -->|Save result crops| Buckets
    
    n8nEngine -->|Webhook triggers| API
    n8nEngine -->|Sync buckets| Buckets
```

---

## 💾 Core Pipeline Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Archiver (User)
    participant Front as Next.js Web App
    participant Back as FastAPI Backend
    participant Storage as Supabase Storage
    participant DB as Supabase DB

    User->>Front: Drags 10 Large Scanned Sheets
    Front->>Storage: Direct Signed URL Upload (raw scans)
    Storage-->>Front: Upload Complete (Paths returned)
    Front->>Back: POST /api/detect/batch {scan_ids}
    loop For each Scan
        Back->>Storage: Fetch Scan Image
        Back->>Back: Run Grounding DINO Detection
        Back->>Back: Apply Overlap & Minimum Size Filter
        Back->>DB: Insert Scan & Draft Photo Bboxes (expires 24h)
    end
    Back-->>Front: Return BBox Coordinates
    Front->>User: Open `/review` panel with Red Frames
    User->>Front: Resize BBox, Add manual frame, click "Finish"
    Front->>Back: POST /api/review/{session_id}/finish {final_bboxes}
    Back->>Back: Crop sub-images + Auto-Rotate + Color Revitalize
    Back->>Storage: Upload cropped JPGs (95% quality)
    Back->>Back: Embed sequential EXIF dates
    Back->>DB: Update public.photos status to "completed"
    Back-->>Front: ZIP Download Link / Google Photos Export OK
    Front->>User: Display success modal and triggers ZIP save
```

---

## 🔒 Security Architecture (OWASP Top 10 Alignments)

- **A1: Broken Access Control:** Every table includes **Row Level Security (RLS)** in Postgres checking `auth.uid() = user_id`.
- **A2: Cryptographic Failures:** High-value photos stored with short-lived **Signed URLs** (expire in 15 minutes). JWTs rotation active.
- **A3: Injection:** SQLAlchemy ORM parameters are bound implicitly to block SQL injection. BBox coordinates validated by Pydantic ranges `[0.0, 1.0]`.
- **A5: Security Misconfiguration:** Strict CSP headers, HSTS preloaded, CORS whitelisted strictly to Vercel production domains.
- **A9: Security Logging:** Structlog redacts PII like user emails and IDs automatically from console prints and logs.
