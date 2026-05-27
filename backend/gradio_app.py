"""
gradio_app.py — Gradio standalone dashboard.
Provides an easy visual interface to test DINO detection & color retouching local-first.
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Add current dir to import paths
sys.path.append(str(Path(__file__).parent))

try:
    import gradio as gr
    _HAS_GRADIO = True
except ImportError:
    _HAS_GRADIO = False


def process_image(img, prompt, conf, overlap_val, run_retouch):
    """Run detection and crop on uploaded image."""
    from app.services.detector import PhotoDetector
    from app.services.retoucher import PhotoRetoucher
    
    if img is None:
        return None, [], "Upload an image first."
        
    detector = PhotoDetector()
    retoucher = PhotoRetoucher()
    
    # Apply color retouch first if selected
    if run_retouch:
        img = retoucher.revitalize_colors(img, strength=1.0)
        
    boxes, scores, labels = detector.detect(img, text_prompt=prompt, confidence_threshold=conf)
    if boxes:
        boxes, scores, labels = detector.remove_overlaps(boxes, scores, labels, overlap_val)
        
    if not boxes:
        return img, [], "No photos detected."
        
    # Draw boxes for visualization
    vis = img.copy()
    draw = ImageDraw.Draw(vis)
    for box in boxes:
        draw.rectangle(box, outline="red", width=4)
        
    # Generate crops
    crops = detector.crop_photos(img, boxes)
    
    status = f"Successfully detected and cropped {len(crops)} photos!"
    return vis, crops, status


def main():
    if not _HAS_GRADIO:
        print("Gradio not installed. Run: pip install gradio")
        return
        
    demo = gr.Interface(
        fn=process_image,
        inputs=[
            gr.Image(type="pil", label="Scanned Page"),
            gr.Textbox(value="an old photo.", label="Detection Text Prompt"),
            gr.Slider(minimum=0.05, maximum=0.95, value=0.15, step=0.05, label="Confidence Threshold"),
            gr.Slider(minimum=0.0, maximum=0.50, value=0.05, step=0.01, label="Overlap Threshold"),
            gr.Checkbox(value=True, label="Apply Auto Color Revitalization (CLAHE)")
        ],
        outputs=[
            gr.Image(type="pil", label="Detections (Red Frames)"),
            gr.Gallery(label="Cropped Output Photos"),
            gr.Textbox(label="Status / Logs")
        ],
        title="Newfkc Photos Local Standalone Dashboard",
        description="Test Grounding DINO detection and CLAHE color adjustments instantly inside your browser.",
    )
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
