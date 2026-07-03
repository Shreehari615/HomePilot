"""
Pytest configuration — ensures the backend/ directory is on sys.path.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path so `import config`, `import tools.X`, etc. work
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
