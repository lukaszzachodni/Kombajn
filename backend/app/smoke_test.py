"""Prosty smoke test infrastruktury KOMBAJN.

Uruchom z hosta po odpaleniu docker-compose:

    python -m backend.app.smoke_test
"""

import json
import urllib.error
import urllib.request


def _get(path: str) -> dict:
    url = f"http://localhost:8000{path}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
            data = resp.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise SystemExit(f"Request to {url} failed: {exc}") from exc
    return json.loads(data)


def main() -> None:
    print("Checking /health ...")
    print(_get("/health"))

    print("Checking /health/storage ...")
    print(_get("/health/storage"))

    print("Checking /health/celery ...")
    print(_get("/health/celery"))

    print("Checking /health/full ...")
    print(json.dumps(_get("/health/full"), indent=2))


if __name__ == "__main__":
    main()

