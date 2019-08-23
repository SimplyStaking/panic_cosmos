from datetime import timedelta


def strfdelta(delta: timedelta, fmt: str) -> str:
    d = {"days": delta.days}
    d["hours"], rem = divmod(delta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)
