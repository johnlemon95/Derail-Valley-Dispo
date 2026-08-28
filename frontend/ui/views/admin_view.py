from nicegui import ui
from frontend.state.app_state import AppState
from frontend.network.api_client import APIClient
from common.enums import JobType, VehicleType, DriveType, UserRole


def render_admin_view(state: AppState, api: APIClient) -> None:
    ui.label("Administration").classes("text-xl font-bold mb-2")

    with ui.tabs() as tabs:
        t_users = ui.tab("Benutzerverwaltung", icon="group")
        t_jobs = ui.tab("Aufträge erstellen", icon="add_task")
        t_fleet = ui.tab("Fuhrpark verwalten", icon="train")

    with ui.tab_panels(tabs, value=t_users).classes("w-full"):
        with ui.tab_panel(t_users):
            _user_management(state, api)
        with ui.tab_panel(t_jobs):
            _job_creation(state, api)
        with ui.tab_panel(t_fleet):
            _fleet_management(state, api)


def _user_management(state: AppState, api: APIClient) -> None:
    async def load_users() -> None:
        try:
            users = await api.get_users()
            user_list.clear()
            with user_list:
                for u in users:
                    with ui.row().classes("items-center gap-2 border-b py-1 w-full"):
                        ui.icon("admin_panel_settings" if u["role"] == "Admin" else "person")
                        ui.label(u["display_name"]).classes("font-semibold")
                        ui.label(f"@{u['username']}").classes("text-grey-6 text-sm")
                        ui.badge(u["role"], color="primary" if u["role"] == "Admin" else "grey")
                        online_color = "positive" if u.get("is_online") else "grey"
                        ui.icon("circle", color=online_color).props("size=xs")
        except Exception as e:
            ui.notify(str(e), type="negative")

    async def create_user() -> None:
        try:
            await api.create_user({
                "username": inp_name.value,
                "display_name": inp_display.value,
                "password": inp_pw.value,
                "role": sel_role.value,
            })
            ui.notify("Benutzer erstellt", type="positive")
            await load_users()
        except Exception as e:
            ui.notify(str(e), type="negative")

    with ui.row().classes("w-full gap-8"):
        with ui.column().classes("w-1/2"):
            ui.label("Spieler anlegen").classes("font-semibold mb-1")
            inp_name = ui.input("Benutzername")
            inp_display = ui.input("Anzeigename")
            inp_pw = ui.input("Passwort", password=True)
            sel_role = ui.select(
                options=[UserRole.OPERATOR, UserRole.ADMIN],
                label="Rolle",
                value=UserRole.OPERATOR,
            )
            ui.button("Anlegen", icon="person_add", on_click=create_user).props("color=primary")
        with ui.column().classes("w-1/2"):
            with ui.row().classes("justify-between w-full"):
                ui.label("Aktive Spieler").classes("font-semibold")
                ui.button(icon="refresh", on_click=load_users).props("flat round dense")
            user_list = ui.column().classes("w-full gap-1")


def _job_creation(state: AppState, api: APIClient) -> None:
    is_custom = {"v": False}

    async def submit() -> None:
        body = {
            "title": inp_title.value,
            "job_type": sel_type.value,
            "origin_track": inp_from.value.upper(),
            "destination_track": inp_to.value.upper(),
            "cargo_description": inp_cargo.value,
            "wagon_count": inp_wagons.value,
            "total_weight_tons": inp_weight.value,
            "total_length_m": inp_length.value,
            "reward": inp_reward.value,
        }
        try:
            if is_custom["v"]:
                await api.create_custom_job(body)
            else:
                await api.create_job(body)
            ui.notify("Auftrag erstellt und gesendet", type="positive")
        except Exception as e:
            ui.notify(str(e), type="negative")

    with ui.column().classes("w-full max-w-lg gap-2"):
        ui.label("Neuen Auftrag anlegen").classes("font-semibold mb-1")
        inp_title = ui.input("Titel")
        sel_type = ui.select(
            options=[e.value for e in JobType],
            label="Auftragstyp",
            value=JobType.FREIGHT,
        )
        inp_from = ui.input("Start-Gleis (z.B. GF-A1L)")
        inp_to = ui.input("Ziel-Gleis (z.B. CS-B2S)")
        inp_cargo = ui.input("Frachtbeschreibung")
        with ui.row().classes("gap-2"):
            inp_wagons = ui.number("Wagenanzahl", value=0, min=0)
            inp_weight = ui.number("Gewicht (t)", value=0.0, min=0)
            inp_length = ui.number("Länge (m)", value=0.0, min=0)
        inp_reward = ui.number("Vergütung ($)", value=0.0, min=0)
        ui.switch("Custom Job (freie Felder)", on_change=lambda e: is_custom.update({"v": e.value}))
        ui.button("Auftrag anlegen", icon="add_task", on_click=submit).props("color=primary")


def _fleet_management(state: AppState, api: APIClient) -> None:
    async def add_vehicle() -> None:
        body = {
            "vehicle_id": inp_vid.value.upper(),
            "vehicle_type": sel_vtype.value,
            "drive_type": sel_drive.value,
        }
        try:
            await api.update_vehicle(inp_vid.value.upper(), body)
            ui.notify("Fahrzeug hinzugefügt", type="positive")
        except Exception as e:
            ui.notify(str(e), type="negative")

    with ui.column().classes("w-full max-w-sm gap-2"):
        ui.label("Fahrzeug hinzufügen").classes("font-semibold mb-1")
        inp_vid = ui.input("Fahrzeug-ID (z.B. DE2-01)")
        sel_vtype = ui.select(options=[e.value for e in VehicleType], label="Typ", value=VehicleType.DE2)
        sel_drive = ui.select(options=[e.value for e in DriveType], label="Antrieb", value=DriveType.DIESEL_ELECTRIC)
        ui.button("Hinzufügen", icon="add", on_click=add_vehicle).props("color=primary")
