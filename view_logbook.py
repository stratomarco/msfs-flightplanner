# ============================================================
# Standalone logbook viewer
# Run: python view_logbook.py
# ============================================================

from rich.console import Console
from logbook import display_recent, display_airport_stats, init_db

console = Console()

init_db()
display_recent(console, n=50)
display_airport_stats(console, top_n=15)