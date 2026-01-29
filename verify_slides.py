"""
Slide Verification Pipeline
Exports PPTX slides via LibreOffice and compares against reference images.
"""

import subprocess
import os
import sys
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(r"C:\Users\User\Documents\0000000\My Classes\DJ Foundations")
PPTX_FILE = BASE_DIR / "DJ_Foundations.pptx"
REFERENCE_DIR = BASE_DIR / "source material" / "images" / "slides"
EXPORT_DIR = BASE_DIR / "slide_exports"
DIFF_DIR = BASE_DIR / "slide_diffs"
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"

def export_slides():
    """Export PPTX to PNG images using LibreOffice."""
    print("=" * 60)
    print("STEP 1: Exporting slides from PPTX via LibreOffice")
    print("=" * 60)

    # Clean export dir
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    EXPORT_DIR.mkdir(exist_ok=True)

    # LibreOffice export command
    # --headless: no GUI
    # --convert-to png: export format
    # --outdir: output directory
    cmd = [
        SOFFICE,
        "--headless",
        "--convert-to", "png",
        "--outdir", str(EXPORT_DIR),
        str(PPTX_FILE)
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False

    print(f"Export output: {result.stdout}")

    # LibreOffice exports to a single file, we need individual slides
    # Check what was exported
    exported = list(EXPORT_DIR.glob("*.png"))
    print(f"Exported files: {exported}")

    return True

def export_slides_via_pdf():
    """Alternative: Export to PDF first, then convert to images."""
    print("=" * 60)
    print("STEP 1: Exporting slides via PDF intermediate")
    print("=" * 60)

    # Clean dirs
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    EXPORT_DIR.mkdir(exist_ok=True)

    pdf_path = EXPORT_DIR / "slides.pdf"

    # Export to PDF
    cmd = [
        SOFFICE,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(EXPORT_DIR),
        str(PPTX_FILE)
    ]

    print(f"Converting to PDF...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False

    # Find the exported PDF
    pdfs = list(EXPORT_DIR.glob("*.pdf"))
    if not pdfs:
        print("ERROR: No PDF generated")
        return False

    pdf_path = pdfs[0]
    print(f"PDF created: {pdf_path}")

    # Convert PDF to PNG images using pdftoppm
    print("Converting PDF pages to PNG...")
    cmd = [
        "pdftoppm",
        "-png",
        "-r", "150",  # DPI
        str(pdf_path),
        str(EXPORT_DIR / "slide")
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"pdftoppm error: {result.stderr}")
        return False

    # Rename to match reference naming (slide-01, slide-02, etc.)
    exported = sorted(EXPORT_DIR.glob("slide-*.png"))
    print(f"Exported {len(exported)} slide images")

    for i, f in enumerate(exported, 1):
        new_name = EXPORT_DIR / f"export_slide_{i:02d}.png"
        f.rename(new_name)
        print(f"  {new_name.name}")

    return True

def compare_slides():
    """Compare exported slides against references."""
    print("\n" + "=" * 60)
    print("STEP 2: Comparing slides against references")
    print("=" * 60)

    try:
        from skimage.metrics import structural_similarity as ssim
        from skimage import io, transform, color
        import numpy as np
    except ImportError as e:
        print(f"ERROR: Missing library: {e}")
        print("Install with: pip install scikit-image")
        return None

    DIFF_DIR.mkdir(exist_ok=True)

    results = []

    for i in range(1, 21):
        ref_path = REFERENCE_DIR / f"slide-{i:02d}.png"
        export_path = EXPORT_DIR / f"export_slide_{i:02d}.png"

        if not ref_path.exists():
            print(f"Slide {i:2d}: MISSING REFERENCE")
            results.append({"slide": i, "status": "missing_ref"})
            continue

        if not export_path.exists():
            print(f"Slide {i:2d}: MISSING EXPORT")
            results.append({"slide": i, "status": "missing_export"})
            continue

        # Load images
        ref_img = io.imread(str(ref_path))
        exp_img = io.imread(str(export_path))

        # Resize export to match reference dimensions
        if ref_img.shape != exp_img.shape:
            exp_img = transform.resize(exp_img, ref_img.shape, anti_aliasing=True)
            exp_img = (exp_img * 255).astype(np.uint8)

        # Convert to grayscale for SSIM
        if len(ref_img.shape) == 3:
            ref_gray = color.rgb2gray(ref_img)
        else:
            ref_gray = ref_img

        if len(exp_img.shape) == 3:
            exp_gray = color.rgb2gray(exp_img)
        else:
            exp_gray = exp_img

        # Calculate SSIM
        score, diff = ssim(ref_gray, exp_gray, full=True, data_range=1.0)

        # Create diff image
        diff_img = (1 - diff) * 255  # Invert so differences are bright
        diff_path = DIFF_DIR / f"diff_slide_{i:02d}.png"
        io.imsave(str(diff_path), diff_img.astype(np.uint8))

        status = "OK" if score > 0.90 else "NEEDS_WORK" if score > 0.75 else "MAJOR_DIFF"
        print(f"Slide {i:2d}: {score:.1%} match - {status}")

        results.append({
            "slide": i,
            "score": score,
            "status": status,
            "diff_path": str(diff_path)
        })

    return results

def generate_report(results):
    """Generate summary report."""
    print("\n" + "=" * 60)
    print("VERIFICATION REPORT")
    print("=" * 60)

    if not results:
        print("No results to report")
        return

    ok = [r for r in results if r.get("status") == "OK"]
    needs_work = [r for r in results if r.get("status") == "NEEDS_WORK"]
    major = [r for r in results if r.get("status") == "MAJOR_DIFF"]
    missing = [r for r in results if "missing" in r.get("status", "")]

    print(f"\nSUMMARY:")
    print(f"  OK (>90% match):      {len(ok)} slides")
    print(f"  Needs work (75-90%):  {len(needs_work)} slides")
    print(f"  Major diff (<75%):    {len(major)} slides")
    print(f"  Missing:              {len(missing)} slides")

    if needs_work or major:
        print(f"\nSLIDES NEEDING ATTENTION:")
        for r in sorted(needs_work + major, key=lambda x: x.get("score", 0)):
            print(f"  Slide {r['slide']:2d}: {r.get('score', 0):.1%} - see {r.get('diff_path', 'N/A')}")

    # Save report
    report_path = BASE_DIR / "verification_report.txt"
    with open(report_path, "w") as f:
        f.write("SLIDE VERIFICATION REPORT\n")
        f.write("=" * 40 + "\n\n")
        for r in results:
            f.write(f"Slide {r['slide']:2d}: {r.get('score', 'N/A'):.1%} - {r['status']}\n")

    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    print("SLIDE VERIFICATION PIPELINE")
    print("=" * 60)
    print(f"PPTX: {PPTX_FILE}")
    print(f"Reference: {REFERENCE_DIR}")
    print()

    # Try PDF method (more reliable for multi-page)
    if export_slides_via_pdf():
        results = compare_slides()
        if results:
            generate_report(results)
    else:
        print("Export failed!")
        sys.exit(1)
