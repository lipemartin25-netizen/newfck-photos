# Premium UI Design System & Architecture: AlbumAI Studio

Design specifications for a premium, world-class user interface matching the aesthetics of modern hyper-growth SaaS platforms like Vercel and Linear.

---

## 🎨 Styling Variables & Design Tokens

### Core Colors (Tailwind Integration)
```css
:root {
  --background: 0 0% 98%;          /* #FAFAFA (Sleek light-grey background) */
  --foreground: 224 71.4% 4.1%;     /* #0F172A (Deep Slate for maximum contrast) */
  
  --primary: 239 84% 67%;          /* #6366F1 (Vibrant Indigo) */
  --primary-hover: 243 75% 59%;    /* #4F46E5 (Deep Indigo) */
  
  --accent: 263 90% 66%;           /* #8B5CF6 (Rich Purple) */
  
  --success: 162 76% 41%;          /* #10B981 (Emerald) */
  --warning: 38 92% 50%;           /* #F59E0B (Amber) */
  --danger: 0 84% 60%;             /* #EF4444 (Red) */
  
  --review-frame: 0 72% 51%;       /* #DC2626 (Strong red for bounding boxes) */
  
  --border: 214.3 31.8% 91.4%;     /* #E2E8F0 */
  --radius: 0.75rem;               /* Premium rounded-xl standard */
}

.dark {
  --background: 222.2 84% 4.9%;    /* #0F172A (Ultra-dark slate) */
  --foreground: 210 40% 98%;       /* #F8FAFC (Ice white) */
  --border: 217.2 32.6% 17.5%;     /* #1E293B */
}
```

---

## ✨ Component Specifications

### 1. UploadDropzone (`UploadDropzone.tsx`)
- **Visuals:** Dashed indigo border with a smooth hover translation (lifts 2px) and a subtle blue halo glow.
- **Micro-animation:** Framer motion `whileHover={{ scale: 1.01 }}` + transition timing `cubic-bezier(0.16, 1, 0.3, 1)`.

### 2. Review BBox Canvas (`CropCanvas.tsx`)
- **Rendering:** Fast canvas scaling rendering via HTML5 `<canvas>` or `Konva.js`.
- **Bounding Boxes:** Sharp red borders (`--review-frame`) at 2px weight, accompanied by 8px round handle anchors at corners for scaling. Includes a hovering badge displaying detection confidence.

### 3. Pricing Table (`PricingTable.tsx`)
- **Structure:** 3 cards featuring an absolute-centered "Most Popular" card with a glowing radial gradient backplate and thick indigo border to command conversion attention.
