from rich.text import Text
from rich.panel import Panel
from rich.live import Live
from rich.console import Group
import os
import sys
import time
import readchar
import requests

from richtype.disclaimer import DISCLAIMER, QUOTES_URL


def fetch_target():
    r = requests.get(QUOTES_URL, timeout=5)
    r.raise_for_status()
    return r.json()["quote"]


def render(typed_text: str, target_text: str):
    """Build a fresh Text comparing typed against TARGET."""
    line = Text()
    for i, ch in enumerate(target_text):
        if i < len(typed_text):
            style = "bold white" if typed_text[i] == ch else "bold red underline"
        else:
            style = "dim"
        line.append(ch, style)
    return Group(DISCLAIMER, Panel(line))


def is_win_condition(typed_text: str, target_text: str):
    return typed_text == target_text


def restart():
    """Dumb restart: replace this process with a fresh instance to get a new quote."""
    os.execv(sys.executable, [sys.executable, *sys.argv])


def main():

    TARGET = fetch_target()
    word_count = len(TARGET.split())
    typed = ""
    start_time = -1
    game_over = False
    did_win = False

    with Live(render(typed, TARGET), refresh_per_second=60) as live:
        while True:
            key = readchar.readchar()

            if key == readchar.key.ESC:
                break
            elif key == readchar.key.CTRL_R:
                live.stop()
                restart()
            elif key == readchar.key.BACKSPACE:
                typed = typed[:-1]
            elif key.isprintable() and len(key) == 1:
                if start_time < 0:  # first keystroke
                    start_time = time.monotonic()
                typed += key

            live.update(render(typed, TARGET))

            if is_win_condition(typed, TARGET):
                did_win = True
                break

        if did_win:
            elapsed = time.monotonic() - float(start_time)
            wpm = int(word_count / (elapsed / 60))
            live.update(
                Group(
                    render(typed, TARGET),
                    Text(f"{wpm} WPM in {elapsed:.1f}s", style="bold green"),
                )
            )


if __name__ == "__main__":
    main()
