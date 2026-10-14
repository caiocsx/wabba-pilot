from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT / "config" / "config.json"
DATA_PATH = ROOT / "data" / "clicked.json"
LOG_PATH = ROOT / "logs" / "wabbajack_autopilot.log"
