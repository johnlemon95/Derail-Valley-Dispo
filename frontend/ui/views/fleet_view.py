from nicegui import ui
from frontend.state.app_state import AppState
from frontend.network.api_client import APIClient

DRIVE_ICON = {
    "Diesel-Elektrik":    "electric_bolt",
    "Diesel-Hydraulik":   "settings",
    "Elektro (Batterie)": "battery_charging_full",
    "Dampf":              "local_fire_department",
    "Manuell":            "directions_walk",
    "Traktionserweiterung": "add_circle",
}


def render_fleet_view(state: AppState, api: APIClient) -> None:
    async def refresh() -> None:
        try:
            vehicles = await api.get_vehicles()
            state.vehicles = vehicles
        except Exception as e:
            ui.notify(f"Fehler beim Laden: {e}", type="negative")
        table.rows.clear()
        table.rows.extend(state.vehicles)
        table.update()

    columns = [
        {"name": "vehicle_id",   "label": "Fahrzeug-ID",  "field": "vehicle_id",   "sortable": True},
        {"name": "vehicle_type", "label": "Typ",           "field": "vehicle_type", "sortable": True},
        {"name": "drive_type",   "label": "Antrieb",       "field": "drive_type"},
        {"name": "current_station", "label": "Station",    "field": "current_station"},
        {"name": "current_track",   "label": "Gleis",      "field": "current_track"},
        {"name": "fuel_percent", "label": "Tank %",        "field": "fuel_percent", "sortable": True},
        {"name": "maintenance_needed", "label": "Wartung", "field": "maintenance_needed"},
        {"name": "assigned_to_username", "label": "Zugewiesen", "field": "assigned_to_username"},
    ]

    with ui.row().classes("w-full justify-between items-center mb-2"):
        ui.label("Fuhrpark-Monitor").classes("text-xl font-bold")
        ui.button(icon="refresh", on_click=refresh).props("flat round dense")

    table = ui.table(columns=columns, rows=state.vehicles, row_key="vehicle_id").classes("w-full")
    table.add_slot("body-cell-fuel_percent", r"""
        <q-td :props="props">
            <q-linear-progress
                :value="props.value / 100"
                :color="props.value > 30 ? 'positive' : 'negative'"
                size="12px" rounded />
            <span class="text-xs">{{ props.value }}%</span>
        </q-td>
    """)
    table.add_slot("body-cell-maintenance_needed", r"""
        <q-td :props="props">
            <q-icon :name="props.value ? 'build' : 'check_circle'"
                    :color="props.value ? 'negative' : 'positive'" size="sm" />
        </q-td>
    """)
