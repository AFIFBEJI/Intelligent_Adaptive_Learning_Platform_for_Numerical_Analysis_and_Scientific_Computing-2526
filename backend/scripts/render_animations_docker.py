r"""
Docker-based Manim renderer (no local Python/LaTeX install needed).

This is the recommended way to render the platform's animations on
Windows when Python 3.14 is the default and pip refuses to build
moderngl / glcontext (no cp314 wheels, MSVC required).

Prerequisites :
  * Docker Desktop running
  * The image manimcommunity/manim:stable pulled :
        docker pull manimcommunity/manim:stable

Usage :
    cd backend
    python scripts/render_animations_docker.py             # render all 4 hero scenes
    python scripts/render_animations_docker.py lagrange    # render only one

Each MP4 lands in :  backend/static/animations/<concept_id>_en.mp4

Why a separate script ?
  * The Docker image already has Manim + LaTeX + ffmpeg + Cairo + Pango
    pre-installed. We just mount the project and run `manim` inside.
  * This sidesteps the Python 3.14 / moderngl wheel compilation hell.
  * We reuse the same MANIM_REGISTRY as the local renderer.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Reuse the registry from the local renderer to avoid duplication.
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from render_animations import BACKEND_DIR, MANIM_REGISTRY, STATIC_DIR  # noqa: E402

DOCKER_IMAGE = "manimcommunity/manim:stable"


def render_one_via_docker(entry) -> bool:
    """Render one scene by mounting the backend dir into the Manim container."""
    if not entry.script_path.exists():
        print(f"  ! Script not found : {entry.script_path}")
        return False

    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    # Path inside the container : /manim is the workdir; we mount backend/ there.
    rel_script = entry.script_path.relative_to(BACKEND_DIR).as_posix()

    # On Windows, Docker needs absolute paths in the form /mnt/c/... or just C:\...
    # Docker Desktop on Windows handles native Windows paths fine for -v.
    backend_abs = str(BACKEND_DIR)

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{backend_abs}:/manim",
        "-w", "/manim",
        DOCKER_IMAGE,
        "manim",
        "-qm",
        "--media_dir", ".manim_media",
        rel_script,
        entry.scene_class,
    ]
    print(f">>> Rendering {entry.concept_id} via Docker ({entry.scene_class})...")
    print(f"    {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"  ! Docker manim failed for {entry.concept_id} : {exc}")
        return False
    except FileNotFoundError:
        print("  ! `docker` not found in PATH. Is Docker Desktop installed and running ?")
        return False

    # Manim writes to backend/.manim_media/videos/<file_name>/720p30/<SceneClass>.mp4
    src_dir = BACKEND_DIR / ".manim_media" / "videos" / entry.file_name / "720p30"
    src = src_dir / f"{entry.scene_class}.mp4"
    if not src.exists():
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
    if shutil.which("docker") is None:
        print("ERROR : `docker` not in PATH. Install/start Docker Desktop first.")
        return 1

    # Quick check that the image is available locally
    check = subprocess.run(
        ["docker", "image", "inspect", DOCKER_IMAGE],
        capture_output=True,
    )
    if check.returncode != 0:
        print(f"Image {DOCKER_IMAGE} not found locally. Pulling now...")
        pull = subprocess.run(["docker", "pull", DOCKER_IMAGE])
        if pull.returncode != 0:
            print("Pull failed. Check your Docker Desktop / network.")
            return 1

    filter_arg = sys.argv[1] if len(sys.argv) > 1 else None
    targets = [
        e for e in MANIM_REGISTRY
        if filter_arg is None or filter_arg in e.concept_id or filter_arg in e.scene_class.lower()
    ]
    if not targets:
        print(f"No registry entry matches : {filter_arg!r}")
        for e in MANIM_REGISTRY:
            print(f"   {e.concept_id}")
        return 1

    succeeded, failed = 0, 0
    for entry in targets:
        if render_one_via_docker(entry):
            succeeded += 1
        else:
            failed += 1

    print()
    print(f"=== Rendered {succeeded}/{len(targets)} animations ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
