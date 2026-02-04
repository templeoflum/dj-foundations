# DJ Foundations

Course materials for DJ Foundations: Song Prep & Basic Mixing.

## Repository Structure

```
DJ Foundations/
├── DJ_Foundations.pptx         # Main presentation
├── docs/                       # GitHub Pages resources site
│   ├── index.html              # Resources page (live at URL below)
│   ├── qr-code.png             # QR code for resources page
│   └── DJ-Foundations-Practice-Guide.pdf
├── source material/            # Source files and reference materials
├── rebuild_slides.py           # PPTX rebuild utility
├── verify_slides.py            # Slide verification pipeline
└── DEVLOG.md                   # Development notes
```

## Live Resources Page

**URL:** https://templeoflum.github.io/dj-foundations/

The resources page is served via GitHub Pages from the `docs/` folder.

### Redirect from Old URL

The previous resources repo (`dj-foundations-resources`) now redirects to the main site.
Existing QR codes pointing to `templeoflum.github.io/dj-foundations-resources/` will continue
to work through this redirect.

## Updating the Resources Page

Edit files in `docs/`, commit, and push:

```bash
git add docs/
git commit -m "Update resources"
git push
```

Changes deploy automatically via GitHub Pages.
