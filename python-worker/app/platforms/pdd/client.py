"""拼多多适配器"""
from datetime import datetime
from typing import List, Optional
import hashlib
import httpx

from app.platforms.base import (
    PlatformAdapter, AuthResult, TokenResult, RawOrder,
    ShipResult, LogisticsTrace
)


class PDDAdapter(PlatformAdapter):
    """拼多多开放平台适配器"""

    API_URL = "https://gw-api.pinduoduo.com/api/router"
    AUTH_URL = "https://mms.pinduoduo.com/open.html"

    async def authorize(self) -> AuthResult:
        from config.settings import settings
        auth_url = (
            f"{self.AUTH_URL}?"
            f"response_type=code&"
            f"client_id={self.app_key}&"
            f"redirect_uri={settings.pdd_callback_url}"
        )
        return AuthResult(success=True, auth_url=auth_url)

    async def handle_callback(self, code: str) -> TokenResult:
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.API_URL, json={
                "type": "pdd.pop.auth.token.create",
                "client_id": self.app_key,
                "client_secret": self.app_secret,
                "code": code,
            })
            data = resp.json()
            if "pop_auth_token_create_response" in data:
                token_data = data["pop_auth_token_create_response"]
                return TokenResult(
                    success=True,
                    access_token=token_data.get("access_token"),
                    refresh_token=token_data.get("refresh_token"),
                )
            return TokenResult(success=False, error=str(data))

    async def refresh_access_token(self) -> TokenResult:
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.API_URL, json={
                "type": "pdd.pop.auth.token.refresh",
                "client_id": self.app_key,
                "client_secret": self.app_secret,
                "refresh_token": self.refresh_token,
            })
            data = resp.json()
            if "pop_auth_token_refresh_response" in data:
                token_data = data["pop_auth_token_refresh_response"]
                return TokenResult(
                    success=True,
                    access_token=token_data.get("access_token"),
                    refresh_token=token_data.get("refresh_token"),
                )
            return TokenResult(success=False, error=str(data))

    async def fetch_orders(self, start_time: datetime, end_time: datetime,
                           page: int = 1, page_size: int = 50) -> List[RawOrder]:
        # TODO: 实现 pdd.order.list.get
        return []

    async def fetch_order_detail(self, platform_order_no: str) -> Optional[RawOrder]:
        # TODO: 实现 pdd.order.information.get
        return None

    async def ship_order(self, platform_order_no: str, company_code: str,
                         tracking_no: str) -> ShipResult:
        # TODO: 实现 pdd.logistics.online.send
        return ShipResult(success=False, error="未实现")

    async def fetch_logistics(self, tracking_no: str, company_code: str) -> List[LogisticsTrace]:
        return []
