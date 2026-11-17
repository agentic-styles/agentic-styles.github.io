"""Build the pattern atlas and field course from their editable sources.

Generated documents and generated diagram copies live only under ``output_root``.
The course template is authored content, rather than a checked-in build product.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COURSE_SOURCE = ROOT / "src" / "pattern-course"


def build(output_root: Path) -> None:
    """Render atlas and course below an already selected site output root."""
    output_root = Path(output_root).resolve()
    atlas = output_root / "atlas"
    course = output_root / "course"
    for generated in (atlas, course):
        if generated.exists():
            shutil.rmtree(generated)
    env = os.environ.copy()
    env["ATLAS_OUTPUT_DIR"] = str(atlas)
    # A CI caller can provide the deployed atlas URL. Local builds intentionally
    # leave canonical URLs absent instead of inventing a public address.
    subprocess.run([sys.executable, str(ROOT / "work" / "build_atlas.py")], cwd=ROOT, env=env, check=True)
    course.mkdir(parents=True)
    shutil.copy2(COURSE_SOURCE / "presentation.html.in", course / "presentation.html")
    shutil.copy2(COURSE_SOURCE / "presentation.html.in", course / "index.html")
    for filename in ("styles.css", "deck.js", "speaker-script.md"):
        shutil.copy2(COURSE_SOURCE / filename, course / filename)
    shutil.copytree(atlas / "diagrams", course / "assets" / "diagrams")
    shutil.copytree(COURSE_SOURCE / "assets", course / "assets", dirs_exist_ok=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    build(parser.parse_args().output)
