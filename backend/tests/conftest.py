import os
import sys
from pathlib import Path

# So `import app`, `import models`, etc. work when pytest is run from
# the backend/ directory or from the repo root.
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("GROQ_MODEL", "openai/gpt-oss-120b")
os.environ.setdefault("PUBLIC_BASE_URL", "http://localhost:8000")
