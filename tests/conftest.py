import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "template"))
sys.path.insert(0, str(ROOT / "skills" / "mcp-oauth-connect" / "scripts"))
