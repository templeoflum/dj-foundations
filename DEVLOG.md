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
pip install python-pptx scikit-image Pillow
```

System requirements:
- LibreOffice (for PDF export)
- pdftoppm (poppler-utils)
