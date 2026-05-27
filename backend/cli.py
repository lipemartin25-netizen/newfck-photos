#!/usr/bin/env python3
"""AlbumAI Studio CLI — Rich terminal interface for photo extraction."""
import os, sys, re, random, argparse, logging, warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
from rich.console import Console
from rich.logging import RichHandler

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*decompression bomb.*")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
Image.MAX_IMAGE_PIXELS = None

console = Console()
logging.basicConfig(level=logging.INFO, format="%(message)s",
                    datefmt="[%m/%d/%y %H:%M:%S]",
                    handlers=[RichHandler(console=console, rich_tracebacks=True)])
log = logging.getLogger("albumai-cli")

EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
CUR_YEAR = datetime.now().year


def main():
    console.print("[bold cyan]" + "=" * 60)
    console.print("[bold cyan]            AlbumAI Studio CLI [/][white]\U0001f4f7 \u2728[/]")
    console.print("[bold cyan]" + "=" * 60 + "\n")

    p = argparse.ArgumentParser(description="AlbumAI Studio CLI")
    p.add_argument("-i", "--input", default="input")
    p.add_argument("-o", "--output", default="output")
    p.add_argument("--text-prompt", default="an old photo.")
    p.add_argument("--single-image", default=None)
    p.add_argument("--preserve-structure", action="store_true")
    p.add_argument("--remove-overlaps", action="store_true", default=True)
    p.add_argument("--no-remove-overlaps", dest="remove_overlaps", action="store_false")
    p.add_argument("--overlap-threshold", type=float, default=0.05)
    p.add_argument("--confidence-threshold", type=float, default=0.15)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--sample-size", type=int, default=None)
    p.add_argument("--device", default=None)
    p.add_argument("--enhance", action="store_true", help="Apply Real-ESRGAN upscale")
    p.add_argument("--upscale-factor", type=int, default=2, choices=[2, 4])
    p.add_argument("--auto-rotate", action="store_true")
    args = p.parse_args()

    from app.services.detector import PhotoDetector
    detector = PhotoDetector(device=args.device, seed=args.seed)

    out_crops = Path(args.output) / "crops"
    out_vis = Path(args.output) / "visualizations"
    out_crops.mkdir(parents=True, exist_ok=True)
    out_vis.mkdir(parents=True, exist_ok=True)

    # Collect files
    inp = Path(args.input)
    if args.single_image:
        files = [Path(args.single_image)]
    else:
        files = sorted(f for root, _, fnames in os.walk(inp)
                       for f in [Path(root) / fn for fn in sorted(fnames)]
                       if f.suffix.lower() in EXTS)

    if args.sample_size and args.sample_size < len(files):
        rng = random.Random(args.seed)
        files = sorted(rng.sample(files, args.sample_size))

    console.print(f"\U0001f680 [bold]Processing {len(files)} images[/]\n")

    total_photos = 0
    year_counts = {}

    for fp in tqdm(files, desc="Processing", unit="image"):
        parent = fp.parent.name
        year = None
        if re.match(r"^\d{4}$", parent) and 1801 <= int(parent) <= CUR_YEAR:
            year = int(parent)
            log.info(f"\U0001f552 Year {year} from folder '{parent}'")

        log.info(f"\U0001f4f7 {fp}")

        try:
            image = Image.open(fp).convert("RGB")
            boxes, scores, labels = detector.detect(
                image, args.text_prompt, confidence_threshold=args.confidence_threshold)
        except Exception as e:
            log.error(f"\u274c {e}")
            continue

        if not boxes:
            log.info("\u26a0\ufe0f No photos detected")
            continue

        log.info(f"\u2705 Found {len(boxes)} photos")

        if args.remove_overlaps:
            boxes, scores, labels = detector.remove_overlaps(
                boxes, scores, labels, args.overlap_threshold)

        crops = detector.crop_photos(image, boxes)
        if not crops:
            continue

        if args.auto_rotate:
            from app.utils.exif_utils import auto_rotate_pil
            crops = [auto_rotate_pil(c) for c in crops]

        for idx, crop in enumerate(crops, 1):
            suffix = f"_{year}" if year else ""
            name = f"{fp.stem}{suffix}_{idx:03d}.jpg"

            if args.preserve_structure and not args.single_image:
                rel = fp.parent.relative_to(inp)
                dest = out_crops / rel
            else:
                dest = out_crops
            dest.mkdir(parents=True, exist_ok=True)

            crop.save(str(dest / name), "JPEG", quality=95)

            if year:
                from app.utils.exif_utils import apply_exif_date
                apply_exif_date(dest / name, year, idx)
                year_counts[year] = year_counts.get(year, 0) + 1

            total_photos += 1

    console.print(f"\n\u2705 [bold green]Done![/] {len(files)} images -> {total_photos} photos")
    if year_counts:
        console.print("\n\U0001f552 [bold]By year:[/]")
        for y in sorted(year_counts):
            console.print(f"  {y}: {year_counts[y]} photos")


if __name__ == "__main__":
    main()
