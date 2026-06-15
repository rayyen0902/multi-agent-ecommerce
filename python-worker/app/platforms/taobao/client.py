"""淘宝 TOP SDK 适配器"""
import hashlib
import time
import json
from datetime import datetime
from typing import List, Optional

import httpx

from app.platforms.base import (
    PlatformAdapter, AuthResult, TokenResult, RawOrder, RawOrderItem,
    ShipResult, LogisticsTrace
)


class TaobaoAdapter(PlatformAdapter):
    """淘宝开放平台适配器"""

    API_URL = "https://eco.taobao.com/router/rest"
    AUTH_URL = "https://auth.taobao.com"

    async def authorize(self) -> AuthResult:
        from config.settings import settings
        auth_url = (
            f"{self.AUTH_URL}/authorize?"
            f"response_type=code&"
            f"client_id={self.app_key}&"
            f"redirect_uri={settings.taobao_callback_url}&"
            f"view=web"
        )
        return AuthResult(success=True, auth_url=auth_url)

    async def handle_callback(self, code: str) -> TokenResult:
        from config.settings import settings
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.API_URL, data={
                "method": "taobao.top.auth.token.create",
                "app_key": self.app_key,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "format": "json",
                "v": "2.0",
                "sign_method": "md5",
                "code": code,
                "uuid": "",
            })
            data = resp.json()
            if "top_auth_token_create_response" in data:
                token_data = data["top_auth_token_create_response"]["token_result"]
                return TokenResult(
                    success=True,
                    access_token=token_data.get("access_token"),
                    refresh_token=token_data.get("refresh_token"),
                    expires_at=datetime.fromtimestamp(
                        int(token_data.get("token_expiry_time", 0)) / 1000
                    ) if token_data.get("token_expiry_time") else None,
                )
            return TokenResult(success=False, error=str(data))

    async def refresh_access_token(self) -> TokenResult:
        async with httpx.AsyncClient() as client:
            params = {
                "method": "taobao.top.auth.token.refresh",
                "app_key": self.app_key,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "format": "json",
                "v": "2.0",
                "sign_method": "md5",
                "refresh_token": self.refresh_token,
            }
            params["sign"] = self._sign(params)
            resp = await client.post(self.API_URL, data=params)
            data = resp.json()
            if "top_auth_token_refresh_response" in data:
                token_data = data["top_auth_token_refresh_response"]["token_result"]
                return TokenResult(
                    success=True,
                    access_token=token_data.get("access_token"),
                    refresh_token=token_data.get("refresh_token"),
                )
            return TokenResult(success=False, error=str(data))

    async def fetch_orders(self, start_time: datetime, end_time: datetime,
                           page: int = 1, page_size: int = 50) -> List[RawOrder]:
        params = {
            "method": "taobao.trades.sold.get",
            "app_key": self.app_key,
            "session": self.access_token,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "v": "2.0",
            "sign_method": "md5",
            "start_created": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_created": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "page_no": str(page),
            "page_size": str(page_size),
            "fields": "tid,status,payment,created,pay_time,buyer_nick,receiver_name,"
                      "receiver_mobile,receiver_state,receiver_city,receiver_district,"
                      "receiver_address,orders",
        }
        params["sign"] = self._sign(params)

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.API_URL, data=params)
            data = resp.json()

        orders = []
        trades = data.get("trades_sold_get_response", {}).get("trades", {}).get("trade", [])
        for trade in trades:
            status_map = {
                "WAIT_BUYER_PAY": "pending",
                "WAIT_SELLER_SEND_GOODS": "paid",
                "WAIT_BUYER_CONFIRM_GOODS": "shipped",
                "TRADE_FINISHED": "completed",
                "TRADE_CLOSED": "closed",
            }
            raw_order = RawOrder(
                platform_order_no=str(trade.get("tid", "")),
                status=status_map.get(trade.get("status", ""), "pending"),
                buyer_name=trade.get("buyer_nick", ""),
                receiver_name=trade.get("receiver_name", ""),
                receiver_phone=trade.get("receiver_mobile", ""),
                receiver_province=trade.get("receiver_state", ""),
                receiver_city=trade.get("receiver_city", ""),
                receiver_district=trade.get("receiver_district", ""),
                receiver_address=trade.get("receiver_address", ""),
                total_amount=float(trade.get("payment", 0)),
                pay_amount=float(trade.get("payment", 0)),
                platform_created_at=self._parse_time(trade.get("created")),
                platform_paid_at=self._parse_time(trade.get("pay_time")),
                raw_data=trade,
            )
            # 解析子订单
            sub_orders = trade.get("orders", {}).get("order", [])
            for sub in sub_orders:
                raw_order.items.append(RawOrderItem(
                    platform_item_id=str(sub.get("oid", "")),
                    product_name=sub.get("title", ""),
                    sku_name=sub.get("sku_properties_name", ""),
                    price=float(sub.get("price", 0)),
                    quantity=int(sub.get("num", 0)),
                    total_price=float(sub.get("total_fee", 0)),
                    image_url=sub.get("pic_path", ""),
                ))
            orders.append(raw_order)

        return orders

    async def fetch_order_detail(self, platform_order_no: str) -> Optional[RawOrder]:
        # TODO: 实现 taobao.trade.fullinfo.get
        return None

    async def ship_order(self, platform_order_no: str, company_code: str,
                         tracking_no: str) -> ShipResult:
        params = {
            "method": "taobao.logistics.online.send",
            "app_key": self.app_key,
            "session": self.access_token,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "v": "2.0",
            "sign_method": "md5",
            "tid": platform_order_no,
            "company_code": company_code,
            "out_sid": tracking_no,
        }
        params["sign"] = self._sign(params)

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.API_URL, data=params)
            data = resp.json()

        if "logistics_online_send_response" in data:
            return ShipResult(success=True)
        error = data.get("error_response", {}).get("sub_msg", "发货失败")
        return ShipResult(success=False, error=error)

    async def fetch_logistics(self, tracking_no: str, company_code: str) -> List[LogisticsTrace]:
        # TODO: 实现 taobao.logistics.trace.search
        return []

    def _sign(self, params: dict) -> str:
        """生成淘宝 API 签名"""
        sorted_params = sorted(params.items())
        sign_str = self.app_secret
        for k, v in sorted_params:
            sign_str += f"{k}{v}"
        sign_str += self.app_secret
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        if not time_str:
            return None
        try:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return None
