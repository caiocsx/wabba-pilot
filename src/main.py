import time
import logging
import keyboard
import threading
import ctypes

from paths import LOG_PATH, DATA_PATH
from collections import defaultdict
from config_loader import load_config
from storage import load_clicked, save_clicked
from ui import get_window, get_buttons
# from focus_guard import run_focus_guard

# ---------------- CONFIG ----------------

config = load_config()

WINDOW_TITLE = config["window_title"]
TARGET_BUTTONS = set(config["target_buttons"])
MAX_CLICK_RETRIES = config["max_click_retries"]
POLL_INTERVAL = config["poll_interval"]
CLICK_COOLDOWN = config["click_cooldown"]

IDLE_THRESHOLD = config["idle_warning_threshold"]
PAUSE_HOTKEY = config["pause_hotkey"]

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


# ---------------- INIT ----------------

DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

clicked = load_clicked()
click_failures = defaultdict(int)
paused = False
last_action = time.time()
idle_logged = False

# ---------------- CONTROL ----------------


def toggle_pause():
    global paused
    paused = not paused
    print(f"[INFO] PAUSED = {paused} ({PAUSE_HOTKEY})")


keyboard.add_hotkey(PAUSE_HOTKEY, toggle_pause)


def get_runtime_id(btn):
    try:
        return tuple(btn.element_info.runtime_id)
    except Exception:
        return None


def prevent_sleep():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def allow_sleep():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)


# ---------------- CORE LOGIC ----------------


def click_button(btn, name):
    logging.info(f"Clicking: {name}")
    try:
        btn.invoke()
        return True
    except Exception:
        logging.warning(f"invoke failed for {name}, retrying with click_input")
        pass
    try:
        btn.click_input()
        return True
    except Exception as e:
        logging.warning(f"click_input also failed for {name}: {e!r}")
        return False


def process_buttons(window):
    global last_action, idle_logged

    for btn in get_buttons(window):
        name = btn.window_text().strip()

        if name not in TARGET_BUTTONS:
            continue

        runtime_id = get_runtime_id(btn)
        if not runtime_id:
            continue

        if runtime_id in clicked:
            continue

        if click_button(btn, name):
            clicked.add(runtime_id)
            save_clicked(clicked)
            last_action = time.time()
            idle_logged = False
        else:
            click_failures[runtime_id] += 1
            if click_failures[runtime_id] >= MAX_CLICK_RETRIES:
                logging.error(
                    f"Giving up on '{name}' after {MAX_CLICK_RETRIES} failed attempts"
                )
                clicked.add(runtime_id)
                save_clicked(clicked)
                del click_failures[runtime_id]
        time.sleep(CLICK_COOLDOWN)


def run_loop():
    global idle_logged
    prevent_sleep()
    logging.info("Autopilot started")

    # guard_stop = threading.Event()
    # guard_thread = threading.Thread(
    #     target=run_focus_guard,
    #     args=(WINDOW_TITLE, lambda: paused, guard_stop),
    #     daemon=True,
    # )
    # guard_thread.start()

    try:
        while True:
            if paused:
                time.sleep(0.2)
                continue

            try:
                window = get_window(WINDOW_TITLE)
                process_buttons(window)

            except Exception as e:
                logging.error(f"Error: {e!r}")

            if time.time() - last_action > IDLE_THRESHOLD and not idle_logged:
                logging.info(
                    f"No clicks in the last {IDLE_THRESHOLD // 60} min (queue may still be downloading)"
                )
                idle_logged = True

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logging.info("Autopilot interrupted by user.")
        print("\n[INFO] Stopped by user (Ctrl+C)")

    finally:
        allow_sleep()
        # guard_stop.set()
        keyboard.unhook_all()
        print("[INFO] Cleaning up...")


# ---------------- ENTRYPOINT ----------------

if __name__ == "__main__":
    run_loop()
