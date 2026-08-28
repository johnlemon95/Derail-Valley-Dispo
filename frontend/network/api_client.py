from typing import List, Optional
import httpx
from frontend.state.app_state import AppState


class APIClient:
    def __init__(self, base_url: str, state: AppState):
        self._base = base_url.rstrip("/")
        self._state = state

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._state.token}"}

    async def login(self, username: str, password: str) -> dict:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self._base}/api/admin/login",
                data={"username": username, "password": password},
            )
            r.raise_for_status()
            return r.json()

    async def get_jobs(self, status: Optional[str] = None) -> List[dict]:
        params = {"job_status": status} if status else {}
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self._base}/api/jobs/", params=params, headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def get_vehicles(self) -> List[dict]:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self._base}/api/fleet/", headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def update_vehicle(self, vehicle_id: str, update: dict) -> dict:
        async with httpx.AsyncClient() as c:
            r = await c.patch(
                f"{self._base}/api/fleet/{vehicle_id}",
                json=update,
                headers=self._headers(),
            )
            r.raise_for_status()
            return r.json()

    async def create_job(self, body: dict) -> dict:
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self._base}/api/admin/jobs", json=body, headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def create_custom_job(self, body: dict) -> dict:
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self._base}/api/admin/jobs/custom", json=body, headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def delete_job(self, job_id: int) -> None:
        async with httpx.AsyncClient() as c:
            r = await c.delete(f"{self._base}/api/admin/jobs/{job_id}", headers=self._headers())
            r.raise_for_status()

    async def get_users(self) -> List[dict]:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self._base}/api/admin/users", headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def create_user(self, body: dict) -> dict:
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self._base}/api/admin/users", json=body, headers=self._headers())
            r.raise_for_status()
            return r.json()
