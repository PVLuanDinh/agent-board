#!/usr/bin/env python3
"""Add (or remove) the keepalive Stop hook in a Claude Code settings file.

    python install_keepalive.py               # ~/.claude/settings.json
    python install_keepalive.py --uninstall
    python install_keepalive.py --settings PATH

Idempotent: an existing keepalive entry is replaced, never duplicated, and every other hook is
kept. The command uses this interpreter's absolute path, so it works whatever `python` means on
the account (python3 on macOS/Linux, a venv, Windows). Backs the file up to <file>.bak first.
"""
import argparse, json, shutil, sys
from pathlib import Path

HOOK = (Path(__file__).resolve().parent / "keepalive.py")
TAG = "keepalive.py"


def is_ours(h: dict) -> bool:
    return TAG in h.get("command", "") or any(TAG in a for a in h.get("args", []))


def apply(settings: Path, uninstall: bool = False) -> str:
    raw = settings.read_text(encoding="utf-8-sig") if settings.exists() else ""
    data = json.loads(raw) if raw.strip() else {}
    stop = data.setdefault("hooks", {}).setdefault("Stop", [])
    for group in stop:
        group["hooks"] = [h for h in group.get("hooks", []) if not is_ours(h)]
    stop[:] = [g for g in stop if g.get("hooks")]
    if not uninstall:
        stop.append({"hooks": [{"type": "command", "command": sys.executable, "args": [str(HOOK)],
                                "timeout": 15, "statusMessage": "agent keepalive check"}]})
    if not stop:
        del data["hooks"]["Stop"]
    if settings.exists():
        shutil.copy2(settings, settings.with_name(settings.name + ".bak"))
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return "removed" if uninstall else "installed"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--settings", type=Path, default=Path.home() / ".claude" / "settings.json")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()
    print(f"keepalive hook {apply(a.settings, a.uninstall)}: {a.settings}")
    print("Active only in sessions started with AGENT_NAME=lead (or AGENT_KEEPALIVE=1); "
          "restart the lead session to load it.")
