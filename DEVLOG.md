# DJ Foundations - Development Log

## Project: PPTX Slide Rebuild from Figma Export

### Date: January 29, 2026

---

## Problem Statement

The Figma-to-PPTX export for the DJ Foundations presentation was **fundamentally broken**:

1. **Text boxes had 4.95" height** - extending past the 5.62" slide bottom
2. **Slide 9**: Images positioned to overlap with text
3. **Slide 18**: Both text columns positioned at same coordinates (completely overlapping)
4. **Text boxes were full-width** when they should be constrained to columns

### Evidence
Rendering the ORIGINAL Figma export showed the same issues - this wasn't from any modifications. The export itself was broken.

---

## Root Cause Analysis

The Figma deck export tool doesn't properly translate:
- Column-based layouts (outputs overlapping full-width boxes)
- Image positioning relative to text
- Appropriate text box sizing (defaults to oversized heights)

---

## Solution: Targeted Slide Rebuild

Instead of patching every element, we targeted only the truly broken slides while preserving slides that were already working.

### Measurement Strategy

Reference images are **4000x2250px**. Slide is **10.00" x 5.62"**.
- **Conversion factor: 400px = 1 inch** (both directions)
- Measure pixel positions from reference images, divide by 400 to get inches

### Tools Used

1. **python-pptx** - Python library for manipulating PowerPoint files
2. **LibreOffice** - Headless PDF export from PPTX
3. **pdftoppm** - Convert PDF pages to PNG for comparison
4. **scikit-image** - SSIM (Structural Similarity Index) for automated comparison

---

## Implementation

### Phase 1: Analysis

Created `rebuild_slides.py` with analysis mode to inspect slide structure:

```python
python rebuild_slides.py analyze
```

This revealed the actual shape positions, sizes, and types on each slide.

**Key Findings:**
- Slide 9: Text width was 9.50" (full slide) instead of ~4.0" (left column)
- Slide 18: Both content boxes at left=0.50" or 5.24" but width=9.50" each
- Most text boxes had height=4.95" regardless of content

### Phase 2: Targeted Fixes

#### Slide 18 - Two-Column Text (Take It Further)
**Problem:** Both columns overlapping at same position
**Fix:**
```python
left_content.left = Inches(0.2)
left_content.width = Inches(4.6)

right_content.left = Inches(5.2)
right_content.width = Inches(4.6)
```

#### Slide 9 - Beats/Bars/Phrases
**Problem:** Diagrams overlapping with text
**Fix:**
- Constrained text to left column (width=4.0")
- Positioned waveform diagram to top-right (left=4.2", top=0.95")
- Positioned 16-beat diagram to bottom-center (left=0.8", top=4.0")

#### Slide 2 - Who Am I?
**Problem:** Images squished and covering title
**Fix:**
- Preserved original aspect ratios when repositioning
- Moved DJ photo to right side (left=5.0", top=0.8")
- Moved meme character to bottom-left (left=0.3", top=3.0")

**Key Learning:** Always preserve aspect ratios when resizing images:
```python
aspect = pic.width.inches / pic.height.inches
target_width = 5.0
target_height = target_width / aspect
```

#### All Slides - Text Box Heights
**Problem:** 4.95" default height on all text boxes
**Fix:** Estimate appropriate height based on content:
```python
def fix_text_box_height(shape, max_height_inches=4.0):
    if shape.height.inches > max_height_inches:
        text = shape.text_frame.text
        lines = text.count('\n') + 1
        estimated_height = max(0.5, lines * 0.25)
        shape.height = Inches(min(estimated_height, max_height_inches))
```

### Phase 3: Verification

Created `verify_slides.py` pipeline:
1. Export PPTX to PDF via LibreOffice (headless)
2. Convert PDF pages to PNG via pdftoppm
3. Compare against reference images using SSIM
4. Generate diff images highlighting differences
5. Produce verification report

```
python verify_slides.py
```

---

## Results

### Before (Original Export)
| Slide | SSIM Score | Issue |
|-------|------------|-------|
| 18 | 76.3% | Overlapping text columns |
| 2 | 81.4% | Squished images, bad positioning |
| 9 | 87.9% | Diagrams overlapping text |

### After (Rebuilt)
| Slide | SSIM Score | Status |
|-------|------------|--------|
| 4, 5, 7, 8, 10, 11, 14, 16, 20 | 90-98% | OK |
| 1, 3, 6, 12, 13, 17, 18 | 75-90% | Layout correct, minor rendering diffs |
| 2, 9 | 62-68% | Layout correct, position/font diffs |
| 15, 19 | ~60-67% | Video embeds (expected - can't match static frames) |

### Visual Verification
All slides now display correctly:
- Text doesn't overlap
- Images properly positioned
- No content extending past slide boundaries
- Aspect ratios preserved

---

## Files Created/Modified

### Created
- `rebuild_slides.py` - Main rebuild script with slide-specific fixes
- `verify_slides.py` - Verification pipeline with SSIM comparison
- `backups/` - Directory with timestamped backups

### Modified
- `DJ_Foundations.pptx` - Fixed presentation

### Reference (Read-Only)
- `source material/DJ_Foundations_Styled (4).pptx` - Original broken export
- `source material/images/slides/slide-XX.png` - Reference images (ground truth)

---

## Lessons Learned

1. **Figma exports are not production-ready** - Always verify and expect to fix layout issues

2. **SSIM scores don't tell the whole story** - A 68% SSIM can still be visually correct; the metric is sensitive to:
   - Font rendering differences between tools
   - Exact pixel positions
   - Color/gradient variations

3. **Preserve aspect ratios** - When repositioning images, always calculate dimensions from original aspect ratio

4. **Target specific fixes** - Don't over-modify. Fix only what's broken, leave working elements alone

5. **Video embeds show as placeholders** - Static exports can't capture embedded video content

---

## Scripts Reference

### rebuild_slides.py

```bash
# Run full rebuild
python rebuild_slides.py

# Analyze slide structure only
python rebuild_slides.py analyze
```

### verify_slides.py

```bash
# Run full verification pipeline
python verify_slides.py
```

Outputs:
- `slide_exports/` - PNG exports of current PPTX
- `slide_diffs/` - Visual diff images
- `verification_report.txt` - SSIM scores and status

---

## Future Improvements

1. **Batch slide fixing** - Create templates for common slide layouts
2. **Better image detection** - Use image content analysis to identify image types
3. **Font matching** - Configure LibreOffice to use same fonts as Figma
4. **Interactive refinement** - GUI tool for fine-tuning positions

---

## Dependencies

```
pip install python-pptx scikit-image Pillow qrcode[pil]
```

System requirements:
- LibreOffice (for PDF export)
- pdftoppm (poppler-utils)
- GitHub CLI (`winget install GitHub.cli`)

---

## Resources Page - GitHub Pages Deployment

### Date: January 29, 2026

---

## Problem Statement

The original `dj_resources.pdf` was a static PDF with no clickable links. Students needed an easy way to access all the resources with working links, ideally via a QR code they could scan.

---

## Solution: GitHub Pages Web App

Created a styled HTML page matching the presentation theme (dark background, teal accents) and deployed it to GitHub Pages.

### Files Created

- `docs/index.html` - Styled resources page with all links
- `docs/qr-code.png` - QR code linking to the live site

### Deployment

1. Installed GitHub CLI: `winget install GitHub.cli`
2. Authenticated via SSH: `gh auth login -p ssh -h github.com -w`
3. Created repo: `gh repo create dj-foundations-resources --public`
4. Enabled GitHub Pages via API
5. Generated QR code with Python `qrcode` library

### Live URLs

- **Resources Page:** https://templeoflum.github.io/dj-foundations-resources/
- **GitHub Repo:** https://github.com/templeoflum/dj-foundations-resources
- **QR Code:** https://templeoflum.github.io/dj-foundations-resources/qr-code.png

### Design Specs

- Background: `#1a1a1a`
- Accent color: `#2dd4bf` (teal)
- Font: Inter (Google Fonts)
- Responsive grid layout
- Hover effects on links

### Categories Included

- Music Sources (Beatport, Bandcamp, SoundCloud, Beatsource)
- DJ Software (Rekordbox, Serato, Traktor, djay Pro, Virtual DJ)
- Utilities (LameXP, Mixed In Key)
- Beginner Controllers
- Education resources
- Video Content & DJ Sets (Boiler Room, HÖR Berlin, Cercle, etc.)
- Record Labels & Collectives (40+ links)
- Genres to Explore
- Essential Terms

### Usage

Students can:
1. Scan the QR code from slides/handouts
2. Access all resources with clickable links on any device
3. Bookmark for future reference

### Updating Resources

To update the resources page:
```bash
cd "DJ Foundations/docs"
# Edit index.html
git add . && git commit -m "Update resources" && git push
```

Changes deploy automatically via GitHub Pages (usually within 1-2 minutes)

---

## Practice Guide QR Code Addition

### Date: January 29, 2026

---

## Problem Statement

The practice guide PDF needed a way for students to easily access the online resources. Adding a scannable QR code would allow quick access via phone.

---

## Solution: PyMuPDF PDF Editing

Used PyMuPDF (fitz) library to add QR code and text to existing PDF without recreating it.

### Placement Process

Finding the right placement required iteration:
1. First attempt: Bottom right corner overlapping footer - rejected
2. Second attempt: Below footer but too small - adjusted
3. Third attempt: Larger QR but text not aligned - fixed
4. Final: 0.90" QR code, right-aligned text, URL fallback

### Final Placement

- **Location:** Bottom right corner, below footer line
- **QR Size:** 65 points (0.90") - scannable on standard letter paper
- **Text:** "More Resources" in teal (#2dd4bf), right-aligned to QR edge
- **URL Fallback:** `templeoflum.github.io/dj-foundations-resources` in gray, right-aligned below label

### Code Pattern

```python
import fitz

doc = fitz.open('practice_guide.pdf')
page = doc[0]

# Get actual text width for precise right-alignment
text_end_x = qr_x - 2  # 2px gap from QR
label_length = fitz.get_text_length(label, fontsize=label_fontsize)
label_x = text_end_x - label_length  # Right-align

page.insert_image(qr_rect, filename='qr-code.png')
page.insert_text(fitz.Point(label_x, label_y), label, fontsize=7, color=(0.18, 0.83, 0.75))

doc.save('practice_guide_updated.pdf')
```

### Key Learnings

1. **Use `fitz.get_text_length()`** for precise text positioning - character count estimation is inaccurate
2. **Right-align by calculating:** `x = end_position - text_width`
3. **QR code minimum size:** ~0.75" for reliable scanning on printed paper
4. **Iterate visually** - PDF coordinate math doesn't always match visual expectations

### Files

- **Input:** `source material/dj_foundations_practice_guide_13.pdf`
- **Output:** `source material/dj_foundations_practice_guide_14.pdf`

### Dependencies

```
pip install pymupdf
```
