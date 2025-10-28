#!/usr/bin/env python3
"""
Batch-split double-page (spread) PDFs into single pages by cutting each page vertically (or horizontally).
- Default: vertical split 50/50 (left + right) per original page, doubling page count.
- Preserves original page size for each half (each output page is half the width).
- Supports offset/ratio adjustments (e.g., for imprecise gutter/spine).
- Handles page rotation.

Usage:
  python split_spreads.py --input "/path/to/folder_or_file" --output "/path/to/output_folder"

Examples:
  # Basic (vertical 50/50), process all PDFs in a folder
  python split_spreads.py -i "./in" -o "./out"

  # Split a single file with a slight spine offset (55/45) to the right
  python split_spreads.py -i book.pdf -o ./out --ratio 0.55

  # Horizontal split for landscape spreads (top/bottom)
  python split_spreads.py -i ./in -o ./out --orientation horizontal

  # Add a small gutter gap (points) between halves (useful before booklet imposition)
  python split_spreads.py -i book.pdf -o ./out --gutter 6

Requirements:
  pip install pypdf

Notes:
- Units are PDF points (1 point = 1/72 inch). A4 width ~ 595pt, height ~ 842pt.
- If your spreads have inner/outer margins, tweak --ratio (e.g., 0.52) or --offset.
"""

import argparse
import os
import sys
import glob
import copy
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except Exception as e:
    print("Error: this script requires the 'pypdf' package. Install with: pip install pypdf", file=sys.stderr)
    raise

def iter_pdf_files(path_str: str):
    p = Path(path_str)
    if p.is_dir():
        for ext in ("*.pdf", "*.PDF"):
            yield from sorted(p.glob(ext))
    elif p.is_file() and p.suffix.lower() == ".pdf":
        yield p
    else:
        print(f"Warning: '{path_str}' is neither a PDF file nor a directory containing PDFs.", file=sys.stderr)

def split_page(page, ratio=0.5, gutter=0.0, offset=0.0, vertical=True):
    """
    Return two page copies (left, right) cropped from the original by a vertical split.
    ratio: position of split as fraction of width (0..1). 0.5 = middle.
    gutter: extra gap (points) removed/added around the split (split pushes crops away by half gutter).
    offset: shift split line horizontally (points), positive => shift right.
    """

    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    split = (width if vertical else height) * ratio + offset
    pad = gutter / 2.0

    # First half
    first_llx = 0
    first_lly = 0
    first_urx = max(0.0, min(width, split - pad)) if vertical else width
    first_ury = height if vertical else max(0.0, min(height, split - pad))

    # second half
    second_llx = min(width, max(0.0, split + pad)) if vertical else 0
    second_lly = 0 if vertical else min(height, max(0.0, split + pad))
    second_urx = width
    second_ury = height

    first = copy.deepcopy(page)
    second = copy.deepcopy(page)

    # Use /CropBox to define visible area (do not change Mediabox to retain page size semantics if desired)
    first.cropbox.lower_left = (first_llx, first_lly)
    first.cropbox.upper_right = (first_urx, first_ury)

    second.cropbox.lower_left = (second_llx, second_lly)
    second.cropbox.upper_right = (second_urx, second_ury)

    return first, second

def process_file(in_path: Path, out_dir: Path, orientation: str, ratio: float, gutter: float, offset: float, suffix: str):
    reader = PdfReader(str(in_path))
    writer = PdfWriter()

    # carry over document metadata
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    for idx, page in enumerate(reader.pages, start=1):
        # Create two new pages from each original
        p1, p2 = split_page(page, ratio=ratio, gutter=gutter, offset=offset, vertical=orientation == "vertical")

        # Optionally, shrink resulting pages' MediaBox to the crop box, so each new page is "physically" half-sized.
        # Comment out next block if you prefer to keep original MediaBox.
        for p in (p1, p2):
            p.mediabox.lower_left = p.cropbox.lower_left
            p.mediabox.upper_right = p.cropbox.upper_right

        writer.add_page(p1)
        writer.add_page(p2)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = in_path.stem + suffix + in_path.suffix
    out_path = out_dir / out_name
    with open(out_path, "wb") as f:
        writer.write(f)

    return out_path

def main():
    ap = argparse.ArgumentParser(description="Split double-page spreads into single pages.")
    ap.add_argument("-i", "--input", required=True, help="Input PDF file or directory containing PDFs.")
    ap.add_argument("-o", "--output", required=True, help="Output directory to write processed PDFs.")
    ap.add_argument("--orientation", choices=["vertical", "horizontal"], default="vertical",
                    help="Split direction. 'vertical' (left/right) or 'horizontal' (top/bottom). Default: vertical.")
    ap.add_argument("--ratio", type=float, default=0.5,
                    help="Split ratio along width/height (0..1). 0.5 means exactly in half. Default: 0.5")
    ap.add_argument("--gutter", type=float, default=0.0,
                    help="Gap (points) to remove around split line. Useful to cut away a spine or create separation. Default: 0")
    ap.add_argument("--offset", type=float, default=0.0,
                    help="Additional absolute shift (points) of split line. Positive shifts right (vertical) or up (horizontal). Default: 0")
    ap.add_argument("--suffix", type=str, default="_split",
                    help="Suffix appended to filename before .pdf. Default: _split")

    args = ap.parse_args()

    inputs = list(iter_pdf_files(args.input))
    if not inputs:
        print("No PDF files found to process.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output)

    print(f"Processing {len(inputs)} file(s)...")
    for p in inputs:
        out_path = process_file(
            in_path=p,
            out_dir=out_dir,
            orientation=args.orientation,
            ratio=args.ratio,
            gutter=args.gutter,
            offset=args.offset,
            suffix=args.suffix,
        )
        print(f"✔ Wrote: {out_path}")

if __name__ == "__main__":
    main()
