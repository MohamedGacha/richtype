from rich.text import Text
from rich.panel import Panel
from rich.live import Live
from rich.console import Group
import os
import sys
import time
import readchar
import requests
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

from richtype.disclaimer import DISCLAIMER, QUOTES_URL


def fetch_target():
    r = requests.get(QUOTES_URL, timeout=5)
    r.raise_for_status()
    return r.json()["quote"]


def render(typed_text: str, target_text: str, progress: Progress):
    """Build a fresh Group comparing typed against TARGET, with the bar."""
    line = Text()
    for i, ch in enumerate(target_text):
        if i < len(typed_text):
            style = "bold white" if typed_text[i] == ch else "bold red underline"
        else:
            style = "dim"
        line.append(ch, style)
    return Group(DISCLAIMER, Panel(line), progress)


def get_win_percentage(typed_text: str, target_text: str):
    """Get the winning percentage for the progress bar."""
    matching_char_count = 0
    for i, ch in enumerate(target_text):
        if i < len(typed_text) and ch == typed_text[i]:
            matching_char_count += 1
        else:
            break
    return matching_char_count * 100 / len(target_text)


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
    did_win = False

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
    )
    task = progress.add_task(description="Game Progress", total=100)

    with Live(render(typed, TARGET, progress), refresh_per_second=60) as live:
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
                if start_time < 0:
                    start_time = time.monotonic()
                typed += key

            progress.update(task, completed=get_win_percentage(typed, TARGET))
            live.update(render(typed, TARGET, progress))

            if is_win_condition(typed, TARGET):
                did_win = True
                break

        if did_win:
            elapsed = time.monotonic() - float(start_time)
            wpm = int(word_count / (elapsed / 60))
            progress.update(task, completed=100)
            live.update(
                Group(
                    render(typed, TARGET, progress),
                    Text(f"{wpm} WPM in {elapsed:.1f}s", style="bold green"),
                )
            )

    


if __name__ == "__main__":
    main()
