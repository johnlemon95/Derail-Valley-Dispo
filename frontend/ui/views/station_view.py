from nicegui import ui
from frontend.state.app_state import AppState
from frontend.network.api_client import APIClient

STATUS_COLOR = {"FREE": "positive", "OCCUPIED": "negative", "RESERVED": "warning"}


def render_station_view(state: AppState, api: APIClient) -> None:
    ui.label("Gleis- & Stations-Dispo").classes("text-xl font-bold mb-4")

    if not state.stations:
        ui.label("Keine Stationsdaten geladen.").classes("text-grey-5")
        return

    for station in state.stations:
        with ui.expansion(f"{station['code']} — {station['name']}", icon="train").classes("w-full"):
            tracks = [v for v in [] if v.get("station_code") == station["code"]]
            if not tracks:
                ui.label("Keine Gleise konfiguriert.").classes("text-grey-5 text-sm")
            for track in tracks:
                color = STATUS_COLOR.get(track["status"], "grey")
                with ui.row().classes("items-center gap-2"):
                    ui.badge(track["track_id"], color=color)
                    ui.label(track["status"])
                    if track.get("occupied_by_job_id"):
                        ui.label(f"Job #{track['occupied_by_job_id']}").classes("text-xs text-grey-6")
