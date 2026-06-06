from rich.text import Text

QUOTES_URL = "https://dummyjson.com/quotes/random"

DISCLAIMER = Text(
    f"Quotes are fetched at random from {QUOTES_URL}. "
    "I am not the author of these quotes and am not responsible for their content.",
    style="dim italic",
)
