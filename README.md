# Wabba Pilot

Automation for Wabbajack that monitors the application window and
automatically clicks configured download buttons.

## Requirements

- Windows
- Python 3.13 or later
- Wabbajack installed and running

## Installation

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

With Wabbajack open, run:

```powershell
python .\src\main.py
```

Press `Ctrl+Alt+P` to pause or resume the automation. Press `Ctrl+C` in the
terminal to stop it.

## Configuration

Options are stored in `config/config.json`:

- `window_title`: title of the monitored window.
- `target_buttons`: buttons that should be clicked.
- `max_click_retries`: maximum number of attempts for each button.
- `poll_interval`: interval between checks, in seconds.
- `click_cooldown`: delay after each click, in seconds.
- `idle_warning_threshold`: time without clicks before a log warning, in seconds.
- `pause_hotkey`: keyboard shortcut used to pause and resume.

Persistent data is stored in `data/`, and logs are stored in `logs/`.