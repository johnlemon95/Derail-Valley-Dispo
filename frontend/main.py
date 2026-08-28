import asyncio
from nicegui import ui, app as nicegui_app
from frontend.state.app_state import AppState
from frontend.network.api_client import APIClient
from frontend.network.ws_client import WSClient
from frontend.ui.views.job_board_view import render_job_board
from frontend.ui.views.fleet_view import render_fleet_view
from frontend.ui.views.station_view import render_station_view
from frontend.ui.views.admin_view import render_admin_view
from config.settings import settings

state = AppState()
api = APIClient(settings.backend_url, state)
ws = WSClient(settings.backend_ws_url, state)


@ui.page("/")
async def login_page():
    with ui.card().classes("absolute-center w-96"):
        ui.label("Derail Valley Dispatcher").classes("text-2xl font-bold text-center w-full mb-4")
        ui.label("Dispo-Pult").classes("text-center text-grey-6 w-full mb-6")
        inp_user = ui.input("Benutzername").classes("w-full")
        inp_pass = ui.input("Passwort", password=True, password_toggle_button=True).classes("w-full")
        err_label = ui.label("").classes("text-negative text-sm")

        async def do_login() -> None:
            err_label.text = ""
            try:
                data = await api.login(inp_user.value, inp_pass.value)
                state.is_logged_in = True
                state.player_id = data["player_id"]
                state.username = data["username"]
                state.display_name = data["display_name"]
                state.role = data["role"]
                state.token = data["access_token"]

                # Load initial data
                state.jobs = await api.get_jobs()
                state.vehicles = await api.get_vehicles()

                # Start WebSocket in background
                asyncio.create_task(ws.connect())

                ui.navigate.to("/dashboard")
            except Exception as e:
                err_label.text = f"Anmeldung fehlgeschlagen: {e}"

        inp_pass.on("keydown.enter", do_login)
        ui.button("Anmelden", on_click=do_login, icon="login").classes("w-full mt-2").props("color=primary")


@ui.page("/dashboard")
async def dashboard():
    if not state.is_logged_in:
        ui.navigate.to("/")
        return

    # Header
    with ui.header(elevated=True).classes("items-center justify-between px-4"):
        ui.label("DV Dispatcher").classes("text-lg font-bold text-white")
        with ui.row().classes("items-center gap-2"):
            conn_dot = ui.icon("circle", color="positive", size="xs")
            ui.label(f"{state.display_name}").classes("text-white text-sm")
            ui.badge(state.role, color="primary" if state.is_admin else "grey")
            ui.button(icon="logout", on_click=_do_logout).props("flat round color=white dense")

    # Toast notifications via WS callback
    def on_ws_event(event: str, data: dict) -> None:
        messages = {
            "job_claimed":    lambda d: f"✅ {d.get('claimed_by_username')} hat Auftrag {d.get('job_id')} angenommen",
            "job_released":   lambda d: f"🔓 Auftrag {d.get('job_id')} ist wieder verfügbar",
            "job_delivered":  lambda d: f"🏁 Auftrag {d.get('job_id')} abgeliefert",
            "job_created":    lambda d: f"🆕 Neuer Auftrag: {d.get('job_id')}",
            "player_connected":    lambda d: f"🟢 {d.get('username', 'Spieler')} verbunden",
            "player_disconnected": lambda d: f"🔴 Spieler #{d.get('player_id')} getrennt",
        }
        if event in messages:
            try:
                ui.notify(messages[event](data), position="top-right", timeout=3000)
            except Exception:
                pass

    ws.set_event_callback(on_ws_event)

    # Main tabs
    with ui.tabs().classes("w-full") as tabs:
        t_jobs = ui.tab("Job Board", icon="assignment")
        t_fleet = ui.tab("Fuhrpark", icon="train")
        t_stations = ui.tab("Stationen", icon="location_on")
        if state.is_admin:
            t_admin = ui.tab("Administration", icon="admin_panel_settings")

    with ui.tab_panels(tabs, value=t_jobs).classes("w-full h-full"):
        with ui.tab_panel(t_jobs):
            render_job_board(state, api, ws)
        with ui.tab_panel(t_fleet):
            render_fleet_view(state, api)
        with ui.tab_panel(t_stations):
            render_station_view(state, api)
        if state.is_admin:
            with ui.tab_panel(t_admin):
                render_admin_view(state, api)


async def _do_logout() -> None:
    ws.disconnect()
    state.reset()
    ui.navigate.to("/")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host="0.0.0.0",
        port=settings.frontend_port,
        title="DV Dispatcher",
        favicon="🚂",
        reload=False,
        dark=True,
    )
