"""HTTP Client 基类 - 封装对 Go Server 和 Python Worker 的调用"""
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class GoServerClient:
    """Go Server REST API 客户端，自动处理认证和统一响应解析"""

    def __init__(self, base_url: str, jwt_token: str = ""):
        self.base_url = base_url.rstrip("/")
        self._jwt_token = jwt_token
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {"Content-Type": "application/json"}
            if self._jwt_token:
                headers["Authorization"] = f"Bearer {self._jwt_token}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    def set_token(self, token: str) -> None:
        """更新 JWT token"""
        self._jwt_token = token
        if self._client and not self._client.is_closed:
            self._client.headers["Authorization"] = f"Bearer {token}"

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get(self, path: str, params: dict = None) -> dict:
        client = await self._get_client()
        resp = await client.get(f"/api/v1{path}", params=params)
        return self._parse_response(resp)

    async def post(self, path: str, json_data: dict = None) -> dict:
        client = await self._get_client()
        resp = await client.post(f"/api/v1{path}", json=json_data)
        return self._parse_response(resp)

    async def put(self, path: str, json_data: dict = None) -> dict:
        client = await self._get_client()
        resp = await client.put(f"/api/v1{path}", json=json_data)
        return self._parse_response(resp)

    async def delete(self, path: str) -> dict:
        client = await self._get_client()
        resp = await client.delete(f"/api/v1{path}")
        return self._parse_response(resp)

    @staticmethod
    def _parse_response(resp: httpx.Response) -> dict:
        """解析 Go Server 统一响应格式 {"code": 0, "message": "success", "data": ...}"""
        try:
            body = resp.json()
        except Exception:
            raise Exception(f"HTTP {resp.status_code}: 响应解析失败")

        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {body.get('message', '请求失败')}")

        if body.get("code", -1) != 0:
            raise Exception(f"API Error: {body.get('message', '未知错误')} (code={body.get('code')})")

        return body.get("data", {})


class PythonWorkerClient:
    """Python Worker API 客户端"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=60.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def trigger_sync(
        self,
        shop_id: int,
        platform: str,
        app_key: str,
        app_secret: str,
        access_token: str,
        sync_type: str = "orders",
    ) -> dict:
        client = await self._get_client()
        resp = await client.post(
            "/api/sync/trigger",
            json={
                "shop_id": shop_id,
                "platform": platform,
                "app_key": app_key,
                "app_secret": app_secret,
                "access_token": access_token,
                "sync_type": sync_type,
            },
        )
        return resp.json()

    async def get_sync_status(self, task_id: str) -> dict:
        client = await self._get_client()
        resp = await client.get(f"/api/sync/status/{task_id}")
        return resp.json()

    async def health_check(self) -> dict:
        client = await self._get_client()
        resp = await client.get("/health")
        return resp.json()
