r"""
Render every Manim scene declared in MANIM_REGISTRY into MP4 files
that the frontend can stream.

Usage :
    cd backend
    .\venv\Scripts\Activate.ps1   # Windows (requires Python 3.11, NOT 3.14)
    pip install -r requirements-manim.txt
    python scripts/render_animations.py            # render all
    python scripts/render_animations.py lagrange   # render one (matches concept_id)

If you can't install Manim locally (Python 3.14 has no wheels yet for some
of its OpenGL deps), use the Docker-based alternative :
    python scripts/render_animations_docker.py

Each MP4 lands in :  backend/static/animations/<concept_id>_en.mp4

System prerequisites for the local renderer :
  * Python 3.11 (NOT 3.14 -- moderngl/glcontext have no wheels for cp314 yet)
  * ffmpeg in PATH
  * LaTeX distribution (MiKTeX on Windows, TeX Live on Linux/Mac)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BACKEND_DIR / "static" / "animations"


@dataclass(frozen=True)
class AnimEntry:
    concept_id: str          # matches the Concept.id in Neo4j
    module_dir: str          # subfolder under manim_scenes/
    file_name: str           # the .py file (without extension)
    scene_class: str         # Manim Scene class to render

    @property
    def script_path(self) -> Path:
        return BACKEND_DIR / "manim_scenes" / self.module_dir / f"{self.file_name}.py"

    @property
    def output_filename(self) -> str:
        return f"{self.concept_id}_en.mp4"


# ============================================================
# Registry : 19 animations (1 per concept in the platform).
# Order = pedagogical order in the curriculum.
# ============================================================
MANIM_REGISTRY: list[AnimEntry] = [
    # ---------- Module 1 : Interpolation (5 concepts) ----------
    AnimEntry("concept_polynomial_basics",   "interpolation", "polynomial_basics",   "PolynomialBasics"),
    AnimEntry("concept_lagrange",            "interpolation", "lagrange",            "LagrangeInterpolation"),
    AnimEntry("concept_divided_differences", "interpolation", "divided_differences", "DividedDifferences"),
    AnimEntry("concept_newton_interpolation","interpolation", "newton_interpolation","NewtonInterpolation"),
    AnimEntry("concept_spline_interpolation","interpolation", "spline_interpolation","SplineInterpolation"),

    # ---------- Module 2 : Numerical Integration (5 concepts) ----------
    AnimEntry("concept_riemann_sums",        "integration",   "riemann_sums",        "RiemannSums"),
    AnimEntry("concept_definite_integrals",  "integration",   "definite_integrals",  "DefiniteIntegrals"),
    AnimEntry("concept_trapezoidal",         "integration",   "trapezoidal",         "TrapezoidalRule"),
    AnimEntry("concept_simpson",             "integration",   "simpson",             "SimpsonsRule"),
    AnimEntry("concept_gaussian_quadrature", "integration",   "gaussian_quadrature", "GaussianQuadrature"),

    # ---------- Module 3 : Approximation & Optimization (5 concepts) ----------
    AnimEntry("concept_least_squares",         "approximation", "least_squares",         "LeastSquaresApproximation"),
    AnimEntry("concept_orthogonal_polynomials","approximation", "orthogonal_polynomials","OrthogonalPolynomials"),
    AnimEntry("concept_minimax_approximation", "approximation", "minimax_approximation", "MinimaxApproximation"),
    AnimEntry("concept_gradient_descent",      "approximation", "gradient_descent",      "GradientDescent"),
    AnimEntry("concept_newton_optimization",   "approximation", "newton_optimization",   "NewtonOptimization"),

    # ---------- Module 4 : Solving Non-linear Equations (4 concepts) ----------
    AnimEntry("concept_bissection",       "root_finding",  "bissection",       "BisectionMethod"),
    AnimEntry("concept_fixed_point",      "root_finding",  "fixed_point",      "FixedPointIteration"),
    AnimEntry("concept_newton_raphson",   "root_finding",  "newton_raphson",   "NewtonRaphson"),
    AnimEntry("concept_secant",           "root_finding",  "secant",           "SecantMethod"),
]


def render_one(entry: AnimEntry) -> bool:
    """Run `manim` to render one scene, then move the MP4 to static/animations/."""
    if not entry.script_path.exists():
        print(f"  ! Script not found : {entry.script_path}")
        return False

    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    # We use medium quality (-qm) for soutenance demo : 720p, 30fps, ~10MB per video.
    # For final hi-res use -qh (1080p) or -qk (4k) but rendering takes much longer.
    cmd = [
        "manim",
        "-qm",
        "--media_dir",
        str(BACKEND_DIR / ".manim_media"),  # temp dir for Manim's intermediate files
        str(entry.script_path),
        entry.scene_class,
    ]
    print(f">>> Rendering {entry.concept_id} ({entry.scene_class})...")
    print(f"    {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, cwd=BACKEND_DIR)
    except subprocess.CalledProcessError as exc:
        print(f"  ! Manim failed for {entry.concept_id} : {exc}")
        return False
    except FileNotFoundError:
        print("  ! `manim` command not found. Did you `pip install -r requirements-manim.txt` ?")
        return False

    # Manim writes to .manim_media/videos/<file>/720p30/<SceneClass>.mp4
    src_dir = BACKEND_DIR / ".manim_media" / "videos" / entry.file_name / "720p30"
    src = src_dir / f"{entry.scene_class}.mp4"
    if not src.exists():
        # fallback : look for any mp4 in that quality folder
        candidates = list(src_dir.glob("*.mp4")) if src_dir.exists() else []
        if not candidates:
            print(f"  ! No output mp4 found in {src_dir}")
            return False
        src = candidates[0]

    dst = STATIC_DIR / entry.output_filename
    shutil.copy2(src, dst)
    print(f"  -> {dst.relative_to(BACKEND_DIR)}  ({dst.stat().st_size // 1024} KB)")
    return True


def main() -> int:
    if shutil.which("manim") is None:
        print("ERROR : `manim` is not in PATH. Run :")
        print("    pip install -r requirements-manim.txt")
        return 1

    filter_arg = sys.argv[1] if len(sys.argv) > 1 else None
    targets = [
        e for e in MANIM_REGISTRY
        if filter_arg is None or filter_arg in e.concept_id or filter_arg in e.scene_class.lower()
    ]
    if not targets:
        print(f"No registry entry matches : {filter_arg!r}")
        print("Available concept_ids :")
        for e in MANIM_REGISTRY:
            print(f"   {e.concept_id}")
        return 1

    succeeded, failed = 0, 0
    for entry in targets:
        if render_one(entry):
            succeeded += 1
        else:
            failed += 1

    print()
    print(f"=== Rendered {succeeded}/{len(targets)} animations ===")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
