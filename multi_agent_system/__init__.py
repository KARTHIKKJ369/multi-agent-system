"""Runtime package namespace for the repository's existing module layout.

The project historically kept feature packages at the repository root.  Extending
``__path__`` preserves that layout while allowing reliable package-relative imports
from Uvicorn, tests, and installed environments.
"""

from pathlib import Path

__path__.append(str(Path(__file__).resolve().parent.parent))
