"""Pre-workshop readiness check. Run from the repository root:

    python src/scripts/check_env.py            # all checks, including the optional Copilot SDK check
    python src/scripts/check_env.py --skip-sdk # skip the (slower) Copilot SDK check
"""

from __future__ import annotations

import asyncio
import importlib
import socket
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))

LEAFLET_URL = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
REQUIRED_MODULES = ["fastapi", "uvicorn", "sqlmodel", "pydantic", "httpx", "pytest"]

results: list[tuple[bool, str, bool]] = []  # (ok, message, optional)


def report(ok: bool, message: str, optional: bool = False) -> None:
    results.append((ok, message, optional))
    icon = "✅" if ok else ("⚠️ " if optional else "❌")
    print(f"{icon} {message}")


def check_python() -> None:
    version = ".".join(map(str, sys.version_info[:3]))
    report(sys.version_info >= (3, 11), f"Python {version} (3.11 or later required)")


def check_dependencies() -> None:
    missing = []
    for name in REQUIRED_MODULES:
        try:
            importlib.import_module(name)
        except ImportError:
            missing.append(name)
    if missing:
        report(False, f"Missing dependencies: {', '.join(missing)}. Run the setup script.")
    else:
        report(True, "Python dependencies import")


def check_database() -> None:
    try:
        from backend.app.db import DB_PATH, db_has_data

        ok = db_has_data()
        hint = "" if ok else " Run: python src/backend/scripts/seed.py"
        report(ok, f"Database has data ({DB_PATH}).{hint}")
    except Exception as error:  # noqa: BLE001 - report any start-up problem
        report(False, f"Database check failed: {error}")


def check_port(port: int = 8000) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        in_use = sock.connect_ex(("127.0.0.1", port)) == 0
    hint = " (is the app already running? Stop it or use --port 8001)" if in_use else ""
    report(not in_use, f"Port {port} is free{hint}")


def check_cdn() -> None:
    try:
        import httpx

        response = httpx.head(LEAFLET_URL, timeout=5, follow_redirects=True)
        report(response.status_code == 200, f"Leaflet CDN reachable ({LEAFLET_URL})")
    except Exception as error:  # noqa: BLE001
        report(False, f"Leaflet CDN not reachable: {error}. See README > Troubleshooting (vendor the files).")


async def _sdk_round_trip() -> str:
    from copilot import CopilotClient
    from copilot.rpc import PermissionDecisionReject

    def deny_tools(request, invocation):  # this check needs no tools
        return PermissionDecisionReject(feedback="Tools are disabled for the readiness check.")

    client = CopilotClient()
    await client.start()
    try:
        auth = await client.get_auth_status()
        if not auth.isAuthenticated:
            raise PermissionError(auth.statusMessage or "not signed in")
        session = await client.create_session(on_permission_request=deny_tools)
        try:
            event = await session.send_and_wait("Reply with exactly one word: pong", timeout=90)
            return event.data.content.strip() if event else ""
        finally:
            await session.disconnect()
    finally:
        await client.stop()


def check_copilot_sdk() -> None:
    label = "Copilot SDK can start and answer a trivial prompt (optional, needed for the assistant step)"
    try:
        importlib.import_module("copilot")
    except ImportError:
        report(False, f"{label}: SDK not installed. Run the setup script.", optional=True)
        return
    try:
        reply = asyncio.run(_sdk_round_trip())
        report(bool(reply), f"{label}: replied {reply!r}", optional=True)
    except PermissionError as error:
        report(False, f"{label}: not signed in ({error}). Sign in to GitHub in VS Code / the "
                      "Copilot CLI, or set GH_TOKEN, and check that you have a Copilot licence.", optional=True)
    except Exception as error:  # noqa: BLE001
        report(False, f"{label}: {type(error).__name__}: {error}. Check sign-in, Copilot licence and "
                      "proxy; try `python -m copilot download-runtime`.", optional=True)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # emoji on Windows consoles
    print("CPH Agentic Hack readiness check\n")
    check_python()
    check_dependencies()
    check_database()
    check_port()
    check_cdn()
    if "--skip-sdk" in sys.argv:
        print("⏭️  Copilot SDK check skipped")
    else:
        check_copilot_sdk()

    required_failures = [m for ok, m, optional in results if not ok and not optional]
    print()
    if required_failures:
        print(f"❌ {len(required_failures)} required check(s) failed. See README > Troubleshooting.")
        return 1
    print("✅ Ready to hack! Start the app: uvicorn backend.app.main:app --app-dir src --reload")
    return 0


if __name__ == "__main__":
    sys.exit(main())
