# Vercel serverless function entry point
import sys
from pathlib import Path

# Add parent directory to path to import api_server
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_server import app

# Export app for Vercel
# Vercel's Python runtime expects the WSGI app to be exported directly


