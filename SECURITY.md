# Security Policy & Threat Model: AlbumAI Studio

We take security and user data privacy seriously. This document outlines our threat modeling, system constraints, and policies for reporting vulnerabilities.

---

## 🛡️ threat Modeling & Security Controls

### 1. Data Isolation & Multi-Tenancy
* **Threat:** A malicious user accesses or manipulates photos/scans belonging to another account.
* **Mitigation:** Strict **Row Level Security (RLS)** is enabled in Supabase Postgres. Every query uses parameterized checks verifying `auth.uid() = user_id`.

### 2. File Upload Exploitation
* **Threat:** Uploading remote execution shells or decompression bomb attacks targeting Pillow/OpenCV nodes.
* **Mitigation:**
  - File size is capped to `50MB` for standard users and verified prior to stream ingestion.
  - Image size pixel limit is un-capped only for authenticated flatbed TIFF runs, but monitored under standard execution threads.
  - Raw binary magic-bytes validation is enforced (we do not trust extension names).

---

## 📈 OWASP Top 10 Alignment

| Vulnerability Category | Mitigation Applied |
|---|---|
| **A01: Broken Access Control** | Supabase RLS enforces absolute isolation on scans, photos, faces, and event clusters. |
| **A03: Injection** | bound parameterized queries inside the SQLAlchemy backend registry. |
| **A05: Security Misconfiguration** | Strict CSP headers, HSTS preloads, CORS whitelist rules. |
| **A09: Security Logging & Monitoring** | Structlog sanitizes user email strings and unique IDs prior to logging. |

---

## 📞 Reporting a Vulnerability

If you discover a security vulnerability, please do not open a public issue. Instead, email our security response team directly at `security@newfkcphotos.com`. We respond to critical reports within 24 hours.
