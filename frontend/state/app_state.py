from dataclasses import dataclass, field
from typing import List, Optional
from common.enums import UserRole


@dataclass
class AppState:
    is_logged_in: bool = False
    player_id: Optional[int] = None
    username: str = ""
    display_name: str = ""
    role: str = UserRole.OPERATOR
    token: str = ""
    jobs: List[dict] = field(default_factory=list)
    vehicles: List[dict] = field(default_factory=list)
    stations: List[dict] = field(default_factory=list)
    connected_players: List[dict] = field(default_factory=list)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def reset(self) -> None:
        self.is_logged_in = False
        self.player_id = None
        self.username = ""
        self.display_name = ""
        self.role = UserRole.OPERATOR
        self.token = ""
        self.jobs.clear()
        self.vehicles.clear()
        self.stations.clear()
        self.connected_players.clear()

    def upsert_job(self, job: dict) -> None:
        for i, j in enumerate(self.jobs):
            if j["id"] == job["id"]:
                self.jobs[i] = job
                return
        self.jobs.append(job)

    def remove_job(self, job_id: int) -> None:
        self.jobs = [j for j in self.jobs if j["id"] != job_id]

    def upsert_vehicle(self, vehicle: dict) -> None:
        for i, v in enumerate(self.vehicles):
            if v["id"] == vehicle["id"]:
                self.vehicles[i] = vehicle
                return
        self.vehicles.append(vehicle)
