# Discovery Notes: AlbumAI Studio v2.0

Comprehensive notes outlining identified user problems, product requirements, and system design specifications for the ultimate album processing platform.

---

## 🔍 Identified User Pain Points & Needs

### 1. Photo Overlap & Low Contrast
Traditional contour-based photo extraction tools fail when:
- Photos overlap slightly inside the album scanner.
- The album page background (e.g., beige or off-white) matches the photo border or edge.
- Photos are faded, presenting low edge gradients.
- **Solution:** Leverage deep learning text-grounded object detectors (`Grounding DINO`), which look for semantic "photo" features rather than pixel-level edges.

### 2. Acid Paper & Fading (Color Deterioration)
Old photo albums deteriorate chemically over time:
- Lignin in acid paper oxidizes, creating a heavy orange/yellow cast over the scan.
- UV exposure fades colored dyes, washing out contrast and saturation.
- Fungus growth leaves brown, splotchy stains.
- **Solution:** Introduce an automated and manual **Color Revitalization** processor applying perfect-reflector white balance, CLAHE contrast adjustments, and targeted yellow-cast suppression.

### 3. Review Fatigue
Users scanning hundreds of album pages don't want to save each photo manually. They need a bulk flow:
- Scan 10-20 large sheets.
- Review all detections at once in a structured UI.
- Adjust, rotate, and crop in a unified canvas with keyboard shortcuts.
- **Solution:** Implement a premium **Batch Review Editor** displaying a thumb sidebar on the left, an interactive multi-bbox editor in the center, and final crops on the right.

### 4. Semantic Search and Retrieval
Once thousands of photos are cropped, organizing them manually is impossible. Users need to group them automatically:
- Group photos containing the same person (Face Clustering).
- Group photos from the same event/location (Temporal + Visual CLIP Clustering).
- **Solution:** Integrate `InsightFace` + `HDBSCAN` for faces, and `OpenCLIP` + `HDBSCAN` for visual-event categorization.

---

## 📋 System Requirements Breakdown

### 🟢 NÍVEL CORE — AI Detection & Local Execution
* **Precision Detections:** Grounding DINO (`IDEA-Research/grounding-dino-base`) with configurable prompt.
* **Overlap Filter:** Non-IoU overlap filter based on *smaller area ratio* (prevents double crops of the same region).
* **Smart EXIF Writing:** Extract year (1801–Current) from directory structure and embed sequentially.
* **CLI Utility:** A standalone rich-terminal interface for power users and developers.

### 🟡 NÍVEL PRO — Web Interface & Enhancement
* **Modern Web Dashboard:** Next.js 14 SPA matching the visual appeal of premium SaaS.
* **Batch Review UI:** Live interactive Canvas (Konva.js) with red bounding boxes.
* **Real-ESRGAN Upscaling:** Denoise + scale 2x/4x for old print scans.
* **Rotation Correction:** Smart hierarchy checking EXIF tags -> OCR text orientation -> Face orientation -> Image statistics.
* **Scanner optimization:** Presets to maximize brightness/contrast of raw scanner prints.
* **Color Revitalization:** Automated CLAHE + Custom White Balance.

### 🔴 NÍVEL ULTRA — Advanced Organizing & Ecosystems
* **Face Clustering:** Automate face grouping and rename clusters.
* **Event Grouping:** Hybrid clustering weighting 70% CLIP visual embeddings + 30% temporal closeness.
* **Card Mode:** Detect trading cards (e.g., Baseball cards, Magic: The Gathering) and postcards using targeted aspect ratios.
* **Deduplication:** Remove near-identical duplicates based on Hamming distance of perceptual hashes (pHash).
* **Cloud Sync:** Direct backup export to Google Photos albums.

---

## 📐 Card Mode Technical Aspect Ratios

| Card Type | Standard Dimension (inches) | Aspect Ratio (W/H) | Target Ratio |
|---|---|---|---|
| **Trading Card** | 2.5 x 3.5 | 0.714 | `~0.71` |
| **Postcard** | 4.0 x 6.0 | 0.667 | `~0.67` |
| **Business Card** | 3.5 x 2.0 | 1.750 | `~1.75` |
| **ID Card** | 3.37 x 2.12 | 1.585 | `~1.59` |
