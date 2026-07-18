#!/usr/bin/env python3
"""Create missing static directory"""

from pathlib import Path

project_root = Path(__file__).parent
static_dir = project_root / "static"
static_dir.mkdir(exist_ok=True)

# Create subdirectories
(static_dir / "css").mkdir(exist_ok=True)
(static_dir / "js").mkdir(exist_ok=True)
(static_dir / "img").mkdir(exist_ok=True)

print("✓ Created static directories")

# Also copy the fixed views
import shutil
src = project_root / "students_views.py"
dst = project_root / "students" / "views.py"
if src.exists():
    shutil.copy2(src, dst)
    print("✓ Updated views.py with namespace fixes")
