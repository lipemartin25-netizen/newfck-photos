# Frontend Product Requirements Document (PRD)

Frontend specifications for **AlbumAI Studio v2.0**.

---

## 🎨 Visual Identity & Brand System

Following the sleek design patterns of **autocropper.io** with advanced batch-editing additions:
- **Palette:** High-contrast Indigo/Violet gradients (`#6366F1` and `#8B5CF6`) for primary CTA surfaces, layered over sleek slate/dark interfaces (`#0F172A`).
- **Typography:** Modern, tech-focused headings using **Geist Sans** (heavy-weight, tracking `-0.04em`), and crisp readable body text in **Inter**.
- **Interactive States:** Smooth Framer Motion card expansions, glassmorphism dropzones, and glowing focus borders.

---

## 🛠️ Main Feature Requirements

### 1. Landing Page (autocropper.io Clone)
* **Hero Banner:** Compelling copy emphasizing auto-cropping, upscale features, and privacy.
* **Try Free Dropzone:** Instantly drops up to 3 image files for quick client-side previews without forcing signup.
* **Pricing Switch:** Monthly / Annual billing toggle (saving 42% on annual) with dynamic badges.

### 2. Batch Review Panel (`/review`)
* **Sidebar:** Infinite scrollable thumbnails displaying all scans, complete with extraction counts and processing state indicators.
* **Konva.js Canvas:** Real-time multi-bounding-box overlays featuring draggable corner handles and double-click box deletion.
* **Toolbar:** Quick actions for 90-degree rotations, AI auto-rotations, and fine-tuning prompts.
* **Crops Panel:** Live cropped thumbnails representing the extracted regions, automatically updated as bounding boxes are resized.

---

## 📈 Quality & Performance Targets
* **Lighthouse Score:** `≥ 95` for Performance, SEO, and Best Practices.
* **A11y Compliance:** WCAG AA (proper ARIA attributes, contrast ratios, and keyboard focus routing).
* **Responsive Breakpoints:** Mobile-first, fully operational on tablet scan-reviews.
* **Theme Support:** Absolute support for light and system-dark settings.
