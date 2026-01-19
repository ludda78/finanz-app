import os

def get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() == "true"

def get_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [v.strip() for v in value.split(",") if v.strip()]

ENV = os.getenv("ENV", "dev")
DEBUG = get_bool("DEBUG")
ENABLE_DOCS = get_bool("ENABLE_DOCS")

FRONTEND_ORIGINS = get_list("FRONTEND_ORIGINS")
