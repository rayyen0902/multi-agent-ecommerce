"""平台适配器抽象基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class AuthResult:
    success: bool
    auth_url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TokenResult:
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class RawOrderItem:
    platform_item_id: str = ""
    product_name: str = ""
    sku_name: str = ""
    price: float = 0.0
    quantity: int = 0
    total_price: float = 0.0
    image_url: str = ""


@dataclass
class RawOrder:
    platform_order_no: str = ""
    status: str = ""
    buyer_name: str = ""
    buyer_message: str = ""
    receiver_name: str = ""
    receiver_phone: str = ""
    receiver_province: str = ""
    receiver_city: str = ""
    receiver_district: str = ""
    receiver_address: str = ""
    total_amount: float = 0.0
    discount_amount: float = 0.0
    shipping_fee: float = 0.0
    pay_amount: float = 0.0
    payment_method: str = ""
    platform_created_at: Optional[datetime] = None
    platform_paid_at: Optional[datetime] = None
    items: List[RawOrderItem] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)


@dataclass
class ShipResult:
    success: bool
    error: Optional[str] = None


@dataclass
class LogisticsTrace:
    time: str = ""
    info: str = ""
    location: str = ""


class PlatformAdapter(ABC):
    """所有平台适配器的抽象基类"""

    def __init__(self, shop_id: int, app_key: str, app_secret: str,
                 access_token: str = "", refresh_token: str = ""):
        self.shop_id = shop_id
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.refresh_token = refresh_token

    @abstractmethod
    async def authorize(self) -> AuthResult:
        """发起OAuth授权，返回授权URL"""
        ...

    @abstractmethod
    async def handle_callback(self, code: str) -> TokenResult:
        """处理OAuth回调，获取Token"""
        ...

    @abstractmethod
    async def refresh_access_token(self) -> TokenResult:
        """刷新Token"""
        ...

    @abstractmethod
    async def fetch_orders(self, start_time: datetime, end_time: datetime,
                           page: int = 1, page_size: int = 50) -> List[RawOrder]:
        """拉取订单列表"""
        ...

    @abstractmethod
    async def fetch_order_detail(self, platform_order_no: str) -> Optional[RawOrder]:
        """拉取订单详情"""
        ...

    @abstractmethod
    async def ship_order(self, platform_order_no: str, company_code: str,
                         tracking_no: str) -> ShipResult:
        """发货回传"""
        ...

    @abstractmethod
    async def fetch_logistics(self, tracking_no: str, company_code: str) -> List[LogisticsTrace]:
        """查询物流轨迹"""
        ...
