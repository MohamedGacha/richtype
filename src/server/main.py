from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import time, statistics
import httpx

app = FastAPI()

# TODO: the multiplayer race server is a work in progress and is NOT ready for use.
#       The single-player CLI (richtype) is the only supported entry point for now.
READY = False

QUOTES_URL = "https://dummyjson.com/quotes/random"
scoreboard = []


async def get_quote():
    """Fetch a random quote from dummyjson, falling back to the default."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(QUOTES_URL)
            r.raise_for_status()
            return r.json()["quote"]
    except (httpx.HTTPError, KeyError):
        return "Error fetching quotes"


@app.websocket("/race")
async def race(ws: WebSocket):
    await ws.accept()
    # The race server is not ready yet; let the client know before doing anything.
    await ws.send_json({"type": "status", "ready": READY})
    quote = await get_quote()
    await ws.send_json({"type": "quote", "quote": quote})

    typed = []
    times = []

    try:
        while True:
            msg = await ws.receive_json()
            now = time.monotonic()
            ch = msg.get("char")

            if ch == "\x08":
                if typed:
                    typed.pop()
            else:
                typed.append(ch)
            times.append(now)

            if "".join(typed) == quote:
                elapsed = times[-1] - times[0]
                wpm = int((len(quote) / 5) / (elapsed / 60))
                intervals = [b - a for a, b in zip(times, times[1:])]
                ok = (
                    len(intervals) > 0
                    and min(intervals) >= 0.02
                    and (len(intervals) < 15 or statistics.pstdev(intervals) >= 0.01)
                    and wpm <= 250
                )
                if ok:
                    scoreboard.append({"wpm": wpm, "elapsed": round(elapsed, 1)})
                await ws.send_json({"type": "result", "wpm": wpm, "valid": ok})
                break
    except WebSocketDisconnect:
        pass
