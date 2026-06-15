"""京东 JOS 适配器"""
from datetime import datetime
from typing import List, Optional
import hashlib
import httpx

from app.platforms.base import (
    PlatformAdapter, AuthResult, TokenResult, RawOrder,
    ShipResult, LogisticsTrace
)


class JDAdapter(PlatformAdapter):
    """京东开放平台适配器"""

    API_URL = "https://api.jd.com/routerjson"
    AUTH_URL = "https://oauth.jd.com"

    async def authorize(self) -> AuthResult:
        from config.settings import settings
        auth_url = (
            f"{self.AUTH_URL}/oauth/authorize?"
            f"app_key={self.app_key}&"
            f"redirect_uri={settings.jd_callback_url}&"
            f"response_type=code&"
            f"state=jd_auth"
        )
        return AuthResult(success=True, auth_url=auth_url)

    async def handle_callback(self, code: str) -> TokenResult:
        async with httpx.AsyncClient() as client:
            # 使用 POST body 传输凭证，避免 app_secret 出现在 URL 日志中
            resp = await client.post(f"{self.AUTH_URL}/oauth/token", json={
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "grant_type": "authorization_code",
                "code": code,
            })
            data = resp.json()
            if "access_token" in data:
                return TokenResult(
                    success=True,
                    access_token=data["access_token"],
                    refresh_token=data.get("refresh_token"),
                )
            return TokenResult(success=False, error=str(data))

    async def refresh_access_token(self) -> TokenResult:
        async with httpx.AsyncClient() as client:
            # 使用 POST body 传输凭证，避免 app_secret 出现在 URL 日志中
            resp = await client.post(f"{self.AUTH_URL}/oauth/token", json={
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            })
            data = resp.json()
            if "access_token" in data:
                return TokenResult(
                    success=True,
                    access_token=data["access_token"],
                    refresh_token=data.get("refresh_token"),
                )
            return TokenResult(success=False, error=str(data))

    async def fetch_orders(self, start_time: datetime, end_time: datetime,
                           page: int = 1, page_size: int = 50) -> List[RawOrder]:
        # TODO: 实现 jingdong.pop.order.search
        return []

    async def fetch_order_detail(self, platform_order_no: str) -> Optional[RawOrder]:
        # TODO: 实现 jingdong.pop.order.get
        return None

    async def ship_order(self, platform_order_no: str, company_code: str,
                         tracking_no: str) -> ShipResult:
        # TODO: 实现 jingdong.pop.order.ship
        return ShipResult(success=False, error="未实现")

    async def fetch_logistics(self, tracking_no: str, company_code: str) -> List[LogisticsTrace]:
        # TODO: 实现物流查询
        return []
