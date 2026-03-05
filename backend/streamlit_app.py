import os
from datetime import datetime, timezone
from typing import Any, Dict

import requests
import streamlit as st
from pydantic import ValidationError

from backend.app.schemas import DatetimeToTimestampRequest


API_BASE = os.getenv("KOMBAJN_API_BASE", "http://api:8000")


def _post_datetime(datetime_iso: str) -> Dict[str, Any]:
    # Walidacja po stronie frontu (ten sam kontrakt, co w API/workerze)
    DatetimeToTimestampRequest(datetime_iso=datetime_iso)

    resp = requests.post(
        f"{API_BASE}/tasks/datetime-to-timestamp",
        json={"datetime_iso": datetime_iso},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _get_task(task_id: str) -> Dict[str, Any]:
    resp = requests.get(f"{API_BASE}/tasks/{task_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    st.set_page_config(
        page_title="KOMBAJN · Datetime → timestamp",
        page_icon="⏱️",
        layout="centered",
    )

    st.title("KOMBAJN · Datetime → timestamp")
    st.caption("Scenariusz testowy: worker przelicza datetime (ISO) na timestamp.")

    now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    with st.form("datetime_form"):
        datetime_iso = st.text_input("Datetime (ISO 8601)", value=now_iso)
        submitted = st.form_submit_button("Wyślij zadanie")

    if submitted and datetime_iso:
        try:
            data = _post_datetime(datetime_iso)
        except ValidationError as exc:
            st.error(f"Błąd walidacji wejścia: {exc}")
        except requests.RequestException as exc:
            st.error(f"Błąd przy tworzeniu zadania: {exc}")
        else:
            st.success("Zadanie wysłane do kolejki.")
            st.json(data)
            st.session_state["last_task_id"] = data.get("task_id")

    st.markdown("---")
    st.subheader("Podgląd stanu zadania")

    default_task_id = st.session_state.get("last_task_id", "")
    task_id = st.text_input("Task ID", value=default_task_id, key="task_status_id")

    if st.button("Odśwież status") and task_id:
        try:
            status = _get_task(task_id)
        except requests.RequestException as exc:
            st.error(f"Błąd przy pobieraniu statusu: {exc}")
        else:
            st.json(status)


if __name__ == "__main__":
    main()

