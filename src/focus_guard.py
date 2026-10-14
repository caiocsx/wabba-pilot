import time
import logging
import win32gui
import win32api
import win32process
import win32con

MAX_RESTORE_RETRIES = 3
RETRY_COOLDOWN = 2.0  # segundos de pausa após desistir de um handle problemático


def _force_set_foreground_window(hwnd):
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    current_thread = win32api.GetCurrentThreadId()
    fg_hwnd = win32gui.GetForegroundWindow()
    fg_thread, _ = win32process.GetWindowThreadProcessId(fg_hwnd)

    if fg_thread == current_thread:
        win32gui.SetForegroundWindow(hwnd)
        return

    win32process.AttachThreadInput(fg_thread, current_thread, True)
    try:
        win32gui.SetForegroundWindow(hwnd)
    finally:
        win32process.AttachThreadInput(fg_thread, current_thread, False)


def run_focus_guard(window_title, is_paused, stop_event, poll_interval=0.15):
    last_user_hwnd = None
    failed_hwnd = None
    failed_count = 0
    blocked_until = 0.0

    while not stop_event.is_set():
        if is_paused():
            time.sleep(0.2)
            continue

        now = time.time()
        wj_hwnd = win32gui.FindWindow(None, window_title)
        fg_hwnd = win32gui.GetForegroundWindow()

        if wj_hwnd and fg_hwnd == wj_hwnd:
            target = last_user_hwnd

            if not target or not win32gui.IsWindow(target):
                pass  # nada válido pra restaurar, não tenta
            elif now < blocked_until:
                pass  # já desistimos desse handle por um tempo
            else:
                try:
                    _force_set_foreground_window(target)
                    failed_hwnd = None
                    failed_count = 0
                except Exception as e:
                    failed_count = failed_count + 1 if target == failed_hwnd else 1
                    failed_hwnd = target

                    if failed_count >= MAX_RESTORE_RETRIES:
                        logging.info(
                            f"focus_guard: giving up on this window for {RETRY_COOLDOWN}s ({e!r})"
                        )
                        blocked_until = now + RETRY_COOLDOWN
                        failed_count = 0
                    else:
                        logging.info(f"focus_guard: could not restore focus: {e!r}")

        elif fg_hwnd:
            last_user_hwnd = fg_hwnd
            failed_hwnd = None
            failed_count = 0

        time.sleep(poll_interval)
