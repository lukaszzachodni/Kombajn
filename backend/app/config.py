from pydantic import BaseModel
from pydantic_settings import BaseSettings


class StoragePaths(BaseModel):
    ssd_root: str = "/data/ssd"
    usb_root: str = "/data/usb"
    hdd_root: str = "/data/hdd"


class Settings(BaseSettings):
    redis_broker_url: str = "redis://redis:6379/0"
    redis_result_backend: str = "redis://redis:6379/1"
    storage: StoragePaths = StoragePaths()

    model_config = {
        "env_prefix": "KOMBAJN_",
        "env_nested_delimiter": "__",
    }


settings = Settings()
