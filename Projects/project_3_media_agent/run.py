"""
run.py
Launch the Media Diversity Watch Agent API server.

Since N8N desktop runs on the same machine, ngrok is not needed.
N8N calls http://localhost:8000/research directly.

Usage:
    python run.py
"""

import uvicorn

PORT = 8000

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Media Diversity Watch Agent")
    print("=" * 60)
    print(f"\n  API:       http://localhost:{PORT}/research")
    print(f"  Docs:      http://localhost:{PORT}/docs")
    print(f"  Health:    http://localhost:{PORT}/")
    print("\n  N8N HTTP Request node is already pointed at:")
    print(f"  http://localhost:{PORT}/research")
    print("\n  Press Ctrl+C to stop.\n")
    print("=" * 60 + "\n")

    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False)
