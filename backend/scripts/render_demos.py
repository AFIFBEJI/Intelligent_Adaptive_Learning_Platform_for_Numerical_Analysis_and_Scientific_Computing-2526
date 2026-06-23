r"""Render the 19 'demo' videos (3Blue1Brown style, real mechanism per method).

Each concept is a stand-alone file in manim_demo/ with two scene classes:
    XxxDemo (EN) / XxxDemoFR (FR).

Output: backend/static/animations/<concept_id>_<lang>.mp4  (the names the
platform already serves) so concept pages pick up the new videos.

Usage (backend/, venv active, manim installed):
    python scripts/render_demos.py                 # all, EN + FR
    python scripts/render_demos.py newton_raphson  # one concept, EN + FR
    python scripts/render_demos.py lagrange fr     # one concept, FR only
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
DEMO_DIR = BACKEND_DIR / "manim_demo"
STATIC_DIR = BACKEND_DIR / "static" / "animations"
MEDIA_DIR = BACKEND_DIR / ".manim_media"

# concept_id -> (file stem in manim_demo/, EN scene class)
REGISTRY = [
    ("concept_polynomial_basics",    "polynomial_basics_demo",   "PolynomialBasicsDemo"),
    ("concept_lagrange",             "lagrange_demo",            "LagrangeDemo"),
    ("concept_divided_differences",  "divided_differences_demo", "DividedDifferencesDemo"),
    ("concept_newton_interpolation", "newton_interpolation_demo","NewtonInterpolationDemo"),
    ("concept_spline_interpolation", "spline_demo",              "SplineDemo"),
    ("concept_riemann_sums",         "riemann_sums_demo",        "RiemannSumsDemo"),
    ("concept_definite_integrals",   "definite_integrals_demo",  "DefiniteIntegralsDemo"),
    ("concept_trapezoidal",          "trapezoidal_demo",         "TrapezoidalDemo"),
    ("concept_simpson",              "simpson_demo",             "SimpsonDemo"),
    ("concept_gaussian_quadrature",  "gaussian_quadrature_demo", "GaussianQuadratureDemo"),
    ("concept_least_squares",        "least_squares_demo",       "LeastSquaresDemo"),
    ("concept_orthogonal_polynomials", "orthogonal_polynomials_demo", "OrthogonalPolynomialsDemo"),
    ("concept_minimax_approximation", "minimax_demo",            "MinimaxDemo"),
    ("concept_gradient_descent",     "gradient_descent_demo",    "GradientDescentDemo"),
    ("concept_newton_optimization",  "newton_optimization_demo", "NewtonOptimizationDemo"),
    ("concept_bissection",           "bissection_demo",          "BisectionDemo"),
    ("concept_fixed_point",          "fixed_point_demo",         "FixedPointDemo"),
    ("concept_newton_raphson",       "newton_raphson_demo",      "NewtonRaphsonDemo"),
    ("concept_secant",               "secant_demo",              "SecantDemo"),
]


def render_one(concept_id, stem, base_cls, lang):
    scene_class = base_cls if lang == "en" else base_cls + "FR"
    scene_file = DEMO_DIR / f"{stem}.py"
    if not scene_file.exists():
        print(f"  ! file missing: {scene_file}")
        return False
    cmd = ["manim", "-qm", "--media_dir", str(MEDIA_DIR), str(scene_file), scene_class]
    print(f">>> {concept_id} [{lang}] ({scene_class})")
    try:
        subprocess.run(cmd, check=True, cwd=BACKEND_DIR)
    except subprocess.CalledProcessError as exc:
        print(f"  ! manim failed: {exc}")
        return False
    except FileNotFoundError:
        print("  ! `manim` not found. pip install -r requirements-manim.txt")
        return False
    vid_root = MEDIA_DIR / "videos" / stem
    matches = sorted(vid_root.glob(f"**/{scene_class}.mp4"),
                     key=lambda p: p.stat().st_mtime, reverse=True)
    if not matches:
        print(f"  ! no output mp4 for {scene_class}")
        return False
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    dst = STATIC_DIR / f"{concept_id}_{lang}.mp4"
    shutil.copy2(matches[0], dst)
    print(f"  -> {dst.relative_to(BACKEND_DIR)}  ({dst.stat().st_size // 1024} KB)")
    return True


def main():
    if shutil.which("manim") is None:
        print("ERROR: manim not in PATH. pip install -r requirements-manim.txt")
        return 1
    args = sys.argv[1:]
    langs = ["en", "fr"]
    if args and args[-1] in ("en", "fr"):
        langs = [args[-1]]
        args = args[:-1]
    cf = args[0] if args else None
    targets = [(c, s, k) for (c, s, k) in REGISTRY
               if cf is None or cf in c or cf in s or cf in k.lower()]
    if not targets:
        print(f"No demo matches {cf!r}.")
        return 1
    ok = fail = 0
    for c, s, k in targets:
        for lang in langs:
            if render_one(c, s, k, lang):
                ok += 1
            else:
                fail += 1
    print(f"\n=== Demos rendered {ok}/{ok + fail} "
          f"({len(targets)} concept(s) x {len(langs)} lang(s)) ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
