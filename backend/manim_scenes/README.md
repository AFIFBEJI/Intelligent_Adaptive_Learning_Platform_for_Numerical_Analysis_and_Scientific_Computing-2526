# Manim animations for the Numera platform

This folder contains Python scripts that produce the **animated visual
explanations** embedded at the top of each concept page on the platform.
They are rendered with [ManimCE](https://docs.manim.community) into MP4
files served as static assets by the FastAPI backend.

## Architecture at a glance

```
backend/
├── manim_scenes/                       <- you are here (Python sources)
│   ├── _base.py                        <- shared NumeraScene + brand palette
│   ├── interpolation/lagrange.py       <- Module 1
│   ├── integration/trapezoidal.py      <- Module 2
│   ├── approximation/gradient_descent.py  <- Module 3
│   └── root_finding/newton_raphson.py  <- Module 4
├── scripts/render_animations.py        <- builds every scene -> MP4
├── static/animations/*.mp4             <- output, served at /static/animations/
└── app/routers/animations.py           <- REST endpoint /animations/{concept_id}
```

The frontend (`content.ts`) calls `GET /animations/<concept_id>?lang=en`,
gets back a URL, and embeds it in a `<video>` element above the lesson.
If 404, the player is simply hidden.

## Render the 4 hero animations (one per module)

### 1. System prerequisites

* **ffmpeg** in PATH (Windows: `winget install Gyan.FFmpeg`)
* **LaTeX**
  * Windows: install [MiKTeX](https://miktex.org/download)
  * macOS: `brew install --cask mactex-no-gui`
  * Linux: `sudo apt-get install texlive-full`

### 2. Python deps

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements-manim.txt
```

### 3. Render every animation

```powershell
python scripts/render_animations.py
```

You will see Manim print compilation logs for each scene. After 1-3
minutes per scene, you should have :

```
backend/static/animations/
├── concept_lagrange_en.mp4          (~6 MB, ~25 s)
├── concept_trapezoidal_en.mp4       (~6 MB, ~25 s)
├── concept_gradient_descent_en.mp4  (~7 MB, ~30 s)
└── concept_newton_raphson_en.mp4    (~7 MB, ~30 s)
```

Render only one, useful while iterating on a script :

```powershell
python scripts/render_animations.py lagrange
```

## Verify it works end-to-end

1. Start the backend (`uvicorn app.main:app --reload`)
2. Open http://localhost:8000/animations — you should see the 4 entries
3. Open http://localhost:8000/animations/concept_lagrange — JSON with the URL
4. Open http://localhost:8000/static/animations/concept_lagrange_en.mp4 — the MP4 streams
5. Start the frontend (`npm run dev`) and open `/content?concept=concept_lagrange`
   → the animation appears above the lesson

## Add a new animation (extending to the other 15 concepts)

The 4 hero scenes cover one concept per module. To extend coverage to the
remaining 15 concepts, follow this template :

### a. Create the scene file

```
backend/manim_scenes/<module>/<concept>.py
```

Skeleton :

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *
from manim_scenes._base import NumeraScene, BRAND_TEAL, ACCENT_AMBER, brand_axes, numera_caption


class MySceneClass(NumeraScene):
    def construct(self):
        self.numera_intro("My Concept Title", "subtitle here")
        # ... your animation code here
        self.numera_outro("My Concept · numera")
```

### b. Register it in render_animations.py

Edit `MANIM_REGISTRY` in `backend/scripts/render_animations.py` :

```python
AnimEntry(
    concept_id="concept_simpson",        # MUST match the Concept.id in Neo4j
    module_dir="integration",
    file_name="simpson",
    scene_class="SimpsonsRule",
),
```

### c. Render and ship

```powershell
python scripts/render_animations.py simpson
git add backend/manim_scenes/integration/simpson.py
git add backend/scripts/render_animations.py
# Note : MP4 outputs are gitignored ; rendering is reproducible.
git commit -m "feat(manim): add Simpson's rule animation"
```

## Concepts covered (19/19) — full coverage

| Module | Concept | Status |
|---|---|---|
| Interpolation | Polynomial Basics | DONE |
| Interpolation | Lagrange | DONE |
| Interpolation | Divided Differences | DONE |
| Interpolation | Newton Interpolation | DONE |
| Interpolation | Spline Interpolation | DONE |
| Integration | Riemann Sums | DONE |
| Integration | Definite Integrals | DONE |
| Integration | Trapezoidal | DONE |
| Integration | Simpson | DONE |
| Integration | Gaussian Quadrature | DONE |
| Approximation | Least Squares | DONE |
| Approximation | Orthogonal Polynomials | DONE |
| Approximation | Minimax | DONE |
| Approximation | Gradient Descent | DONE |
| Approximation | Newton Optimization | DONE |
| Root finding | Bissection | DONE |
| Root finding | Fixed Point | DONE |
| Root finding | Newton-Raphson | DONE |
| Root finding | Secant | DONE |

## Bilingual (FR/EN) animations — future work

For now, every animation is rendered in English only. The platform is
bilingual but the Manim scenes only contain :
  * Mathematical formulas (universal, identical FR/EN)
  * Short captions (e.g., "Each step moves opposite to the gradient")

To produce a French version of an existing scene, duplicate the script
with `_fr` suffix, replace the captions, register it under
`concept_id="..._fr"`, and re-run the render script. The
`/animations/{concept_id}?lang=fr` endpoint will fall back to the English
MP4 if the French one isn't built yet, so you can deploy bilingual
incrementally without breaking the frontend.

## Why not pre-render in CI ?

LaTeX + Manim install ~2 GB of dependencies and renders take 1-3 min per
scene. Putting that in GitHub Actions would slow down every PR by
10-15 min for no benefit. We keep the rendered MP4s checked in (or in a
release artifact) and rebuild only when a script changes.
