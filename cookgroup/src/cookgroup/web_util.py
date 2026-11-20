from datetime import datetime
from zoneinfo import ZoneInfo

MAD = ZoneInfo("Europe/Madrid")


def madrid(ts) -> str:
    if ts is None or ts == "":
        return "—"
    d = datetime.fromtimestamp(ts, MAD) if isinstance(ts, (int, float)) else datetime.fromisoformat(ts).astimezone(MAD)
    return d.strftime("%d/%m/%Y %H:%M")
