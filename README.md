# split-pdf-spreads
A simple script to split pdf with spreads (2 pages of a book visible at a time) into individual pages. This allows you to print and collate the book correctly.

Useful for example for printing Gemini storybooks

Batch-split double-page (spread) PDFs into single pages by cutting each page vertically (or horizontally).
- Default: vertical split 50/50 (left + right) per original page, doubling page count.
- Preserves original page size for each half (each output page is half the width).
- Supports offset/ratio adjustments (e.g., for imprecise gutter/spine).
- Handles page rotation.

# Usage:
  ```
python split_spreads.py --input "/path/to/folder_or_file" --output "/path/to/output_folder"
```

# Examples:
```

  # Basic (vertical 50/50), process all PDFs in a folder
  python split_spreads.py -i "./in" -o "./out"

  # Split a single file with a slight spine offset (55/45) to the right
  python split_spreads.py -i book.pdf -o ./out --ratio 0.55

  # Horizontal split for landscape spreads (top/bottom)
  python split_spreads.py -i ./in -o ./out --orientation horizontal

  # Add a small gutter gap (points) between halves (useful before booklet imposition)
  python split_spreads.py -i book.pdf -o ./out --gutter 6
```

# Requirements:
  ```
pip install pypdf
```

# Notes:
- Units are PDF points (1 point = 1/72 inch). A4 width ~ 595pt, height ~ 842pt.
- If your spreads have inner/outer margins, tweak --ratio (e.g., 0.52) or --offset.
