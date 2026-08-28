"""Launcher – run as:  python main.py server | client"""
import subprocess
import sys


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in {"server", "client"}:
        print("Usage: python main.py [server|client]")
        print("  server  –  Start FastAPI backend (Host only)")
        print("  client  –  Start NiceGUI frontend (all players)")
        sys.exit(1)

    if sys.argv[1] == "server":
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "backend.main:app",
             "--host", "0.0.0.0", "--port", "8000", "--reload"],
            check=True,
        )
    else:
        subprocess.run([sys.executable, "frontend/main.py"], check=True)


if __name__ == "__main__":
    main()
