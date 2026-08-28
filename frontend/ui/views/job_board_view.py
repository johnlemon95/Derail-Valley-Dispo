from nicegui import ui
from frontend.state.app_state import AppState
from frontend.network.api_client import APIClient
from frontend.network.ws_client import WSClient

STATUS_COLOR = {
    "UNCLAIMED":  "positive",
    "CLAIMED":    "warning",
    "IN_TRANSIT": "info",
    "DELIVERED":  "grey",
    "CANCELLED":  "negative",
}
STATUS_LABEL = {
    "UNCLAIMED":  "VERFÜGBAR",
    "CLAIMED":    "BELEGT",
    "IN_TRANSIT": "IN TRANSPORT",
    "DELIVERED":  "ERLEDIGT",
    "CANCELLED":  "STORNIERT",
}


def render_job_board(state: AppState, api: APIClient, ws: WSClient) -> None:
    detail_col = None
    selected_job: dict = {}

    def refresh_list() -> None:
        job_list.clear()
        with job_list:
            for job in state.jobs:
                _job_card(job)

    def show_detail(job: dict) -> None:
        selected_job.clear()
        selected_job.update(job)
        detail_col.clear()
        with detail_col:
            _job_detail(job)

    def _job_card(job: dict) -> None:
        color = STATUS_COLOR.get(job["status"], "grey")
        is_mine = job.get("claimed_by_player_id") == state.player_id
        with ui.card().classes("w-full cursor-pointer hover:shadow-md").on("click", lambda j=job: show_detail(j)):
            with ui.row().classes("w-full justify-between items-center"):
                with ui.column().classes("gap-0"):
                    ui.label(job["job_id"]).classes("font-bold text-base")
                    ui.label(f"{job['origin_track']}  ➔  {job['destination_track']}").classes("text-sm text-grey-7")
                with ui.row().classes("gap-1 items-center"):
                    if job.get("is_custom"):
                        ui.badge("CUSTOM", color="purple")
                    ui.badge(STATUS_LABEL.get(job["status"], job["status"]), color=color)
            with ui.row().classes("justify-between w-full"):
                ui.label(f"${job['reward']:.0f}").classes("text-green-700 font-semibold")
                if job.get("claimed_by_username"):
                    owner = "Du" if is_mine else job["claimed_by_username"]
                    ui.label(f"👤 {owner}").classes("text-xs text-grey-6")

    def _job_detail(job: dict) -> None:
        ui.label("Auftrags-Details").classes("text-lg font-bold mb-2")
        ui.separator()
        with ui.grid(columns=2).classes("w-full gap-x-4 gap-y-1 mt-2"):
            ui.label("ID:").classes("font-semibold")
            ui.label(job["job_id"])
            ui.label("Typ:").classes("font-semibold")
            ui.label(job["job_type"])
            ui.label("Von:").classes("font-semibold")
            ui.label(job["origin_track"])
            ui.label("Nach:").classes("font-semibold")
            ui.label(job["destination_track"])
            ui.label("Fracht:").classes("font-semibold")
            ui.label(job["cargo_description"] or "–")
            ui.label("Wagen:").classes("font-semibold")
            ui.label(str(job["wagon_count"]))
            ui.label("Gewicht:").classes("font-semibold")
            ui.label(f"{job['total_weight_tons']} t")
            ui.label("Länge:").classes("font-semibold")
            ui.label(f"{job['total_length_m']} m")
            ui.label("Vergütung:").classes("font-semibold")
            ui.label(f"${job['reward']:.0f}").classes("text-green-700")
        ui.separator().classes("my-2")
        _action_buttons(job)

    def _action_buttons(job: dict) -> None:
        is_mine = job.get("claimed_by_player_id") == state.player_id
        can_release = is_mine or state.is_admin

        if job["status"] == "UNCLAIMED":
            ui.button("Auftrag annehmen", icon="check_circle", color="positive",
                      on_click=lambda j=job: _do_claim(j)).classes("w-full mt-2")
        elif job["status"] == "CLAIMED" and is_mine:
            ui.button("In Transport setzen", icon="directions_railway", color="info",
                      on_click=lambda j=job: _do_transit(j)).classes("w-full mt-2")
            if can_release:
                ui.button("Auftrag freigeben", icon="undo", color="warning",
                          on_click=lambda j=job: _do_release(j)).classes("w-full mt-1")
        elif job["status"] == "IN_TRANSIT" and is_mine:
            ui.button("Als erledigt markieren", icon="task_alt", color="primary",
                      on_click=lambda j=job: _do_deliver(j)).classes("w-full mt-2")
        elif job["status"] == "CLAIMED" and not is_mine:
            ui.label(f"Belegt von {job['claimed_by_username']}").classes("text-grey-6 text-sm mt-2")
            if state.is_admin:
                ui.button("Freigeben (Admin)", icon="admin_panel_settings", color="negative",
                          on_click=lambda j=job: _do_release(j)).classes("w-full mt-1")

    async def _do_claim(job: dict) -> None:
        await ws.claim_job(job["id"])

    async def _do_release(job: dict) -> None:
        await ws.release_job(job["id"])

    async def _do_deliver(job: dict) -> None:
        await ws.deliver_job(job["id"])

    async def _do_transit(job: dict) -> None:
        # IN_TRANSIT is set by the player starting the run – treated as claim_result ack here
        pass

    with ui.row().classes("w-full gap-4 h-full"):
        # Left: job list
        with ui.column().classes("w-1/2 gap-2"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Auftrags-Pool").classes("text-xl font-bold")
                ui.button(icon="refresh", on_click=refresh_list).props("flat round dense")
            job_list = ui.column().classes("w-full gap-2 overflow-y-auto")

        # Right: detail panel
        with ui.column().classes("w-1/2"):
            detail_col = ui.column().classes("w-full")
            with detail_col:
                ui.label("← Auftrag auswählen").classes("text-grey-5 mt-8 text-center w-full")

    # Register WS callback to refresh list on any job event
    ws.set_event_callback(lambda event, _: refresh_list() if "job" in event else None)
    refresh_list()
