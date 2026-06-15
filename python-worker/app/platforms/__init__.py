"""平台适配器注册表"""
from app.platforms.base import PlatformAdapter
from app.platforms.taobao.client import TaobaoAdapter
from app.platforms.jd.client import JDAdapter
from app.platforms.pdd.client import PDDAdapter

PLATFORM_REGISTRY: dict[str, type[PlatformAdapter]] = {
    "taobao": TaobaoAdapter,
    "jd": JDAdapter,
    "pdd": PDDAdapter,
}


def get_adapter(platform: str, shop_id: int, app_key: str, app_secret: str,
                access_token: str = "", refresh_token: str = "") -> PlatformAdapter:
    """获取平台适配器实例"""
    adapter_cls = PLATFORM_REGISTRY.get(platform)
    if not adapter_cls:
        raise ValueError(f"不支持的平台: {platform}")
    return adapter_cls(
        shop_id=shop_id,
        app_key=app_key,
        app_secret=app_secret,
        access_token=access_token,
        refresh_token=refresh_token,
    )
