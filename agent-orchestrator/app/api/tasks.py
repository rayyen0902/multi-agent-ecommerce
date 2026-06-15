"""任务管理端点 - 查询历史会话和任务状态"""
import logging

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException

from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["tasks"])

# 全局黑板服务，在 main.py 中注入
_blackboard = None


def set_dependencies(blackboard):
    global _blackboard
    _blackboard = blackboard


def _get_user_id(authorization: str = Header(default="")) -> int:
    """从 Authorization header 中提取 user_id"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证信息")
    token = authorization[7:]
    try:
        payload = jwt.decode(
            token,
            settings.services.jwt_secret,
            algorithms=["HS256"],
        )
        return payload.get("user_id", 0)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token 无效")


@router.get("/sessions")
async def list_sessions(
    page: int = 1,
    page_size: int = 20,
    user_id: int = Depends(_get_user_id),
):
    """获取用户的对话历史"""
    offset = (page - 1) * page_size
    sessions = await _blackboard.get_session_history(
        user_id=user_id, limit=page_size, offset=offset
    )
    return {
        "code": 0,
        "message": "success",
        "data": {"list": sessions, "page": page, "page_size": page_size},
    }


@router.get("/sessions/{session_id}")
async def get_session_detail(
    session_id: str,
    user_id: int = Depends(_get_user_id),
):
    """获取指定会话的黑板条目（完整对话记录）"""
    entries = await _blackboard.get_session_entries(session_id)
    return {
        "code": 0,
        "message": "success",
        "data": entries,
    }
