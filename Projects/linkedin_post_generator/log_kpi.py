"""
Wöchentliches KPI-Logging für das Inbound-Content-System.

Einmal pro Woche ausführen (z.B. freitagabends):
    python log_kpi.py

Fragt nach den 4 Zahlen aus dem Webinar-Funnel und hängt sie an kpi_log.json an.
Die nächste Freitags-Mail zeigt dann den aktuellen Stand gegen die Ziele:
- 100.000+ Impressions in 90 Tagen
- 15-25 Eisbrecher-Nachrichten pro Woche
- 3+ Termine pro Woche
- >50% Closing-Rate
"""

import json
import os
from datetime import datetime

KPI_LOG_FILE = os.path.join(os.path.dirname(__file__), "kpi_log.json")


def load_log() -> list[dict]:
    if not os.path.exists(KPI_LOG_FILE):
        return []
    try:
        with open(KPI_LOG_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_log(log: list[dict]) -> None:
    with open(KPI_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def ask_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return 0
        try:
            return int(raw)
        except ValueError:
            print("Bitte eine Zahl eingeben (oder leer lassen für 0).")


def main():
    print("KPI-Log für diese Woche (Enter = 0)\n")
    impressions = ask_int("LinkedIn-Impressions diese Woche: ")
    eisbrecher_sent = ask_int("Eisbrecher-Nachrichten tatsächlich verschickt: ")
    termine = ask_int("Termine gebucht: ")
    abschluesse = ask_int("Davon abgeschlossen (Kunde gewonnen): ")

    log = load_log()
    log.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "impressions": impressions,
        "eisbrecher_sent": eisbrecher_sent,
        "termine": termine,
        "abschluesse": abschluesse,
    })
    save_log(log)
    print(f"\nGespeichert in {KPI_LOG_FILE}. Steht in der nächsten Freitags-Mail.")


if __name__ == "__main__":
    main()
