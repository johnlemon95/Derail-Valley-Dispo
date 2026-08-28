from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 8080

    # Database
    database_url: str = "sqlite:///./dv_dispatcher.db"

    # Auth
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_ENV_FILE"
    token_expire_hours: int = 24

    # Game logic
    disconnect_timeout_seconds: int = 120  # auto-release job after 2 min disconnect

    @property
    def backend_url(self) -> str:
        return f"http://localhost:{self.backend_port}"

    @property
    def backend_ws_url(self) -> str:
        return f"ws://localhost:{self.backend_port}"


settings = Settings()
