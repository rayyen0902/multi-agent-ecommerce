"""对话 WebSocket 端点"""
import json
import logging
import uuid

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局工作流实例，在 main.py 中注入
_workflow = None
_blackboard = None


def set_dependencies(workflow, blackboard):
    global _workflow, _blackboard
    _workflow = workflow
    _blackboard = blackboard


def _verify_token(token: str) -> dict | None:
    """验证 JWT token，返回 payload"""
    try:
        payload = jwt.decode(
            token,
            settings.services.jwt_secret,
            algorithms=["HS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token 已过期")
        return None
    except jwt.InvalidTokenError:
        logger.warning("JWT token 无效")
        return None


@router.websocket("/api/agent/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(default=""),
):
    """对话 WebSocket 端点

    协议:
    - 客户端发送: {"type": "user_message", "session_id": "...", "content": "..."}
    - 服务端推送:
      - {"type": "agent_response", "session_id": "...", "content": "..."}
      - {"type": "task_progress", "session_id": "...", "content": "...", "metadata": {...}}
      - {"type": "error", "session_id": "...", "content": "错误信息"}
    """
    await websocket.accept()

    # 验证 token
    payload = _verify_token(token)
    if not payload:
        await websocket.send_json({
            "type": "error",
            "session_id": "",
            "content": "认证失败，请重新登录",
        })
        await websocket.close(code=4001)
        return

    user_id = payload.get("user_id", 0)
    logger.info(f"WebSocket 连接: user_id={user_id}")

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")
            session_id = data.get("session_id", "") or str(uuid.uuid4())
            user_input = data.get("content", "")

            if msg_type != "user_message":
                await websocket.send_json({
                    "type": "error",
                    "session_id": session_id,
                    "content": f"不支持的消息类型: {msg_type}",
                })
                continue

            if not user_input.strip():
                await websocket.send_json({
                    "type": "error",
                    "session_id": session_id,
                    "content": "请输入内容",
                })
                continue

            # 推送进度：意图识别中
            await websocket.send_json({
                "type": "task_progress",
                "session_id": session_id,
                "content": "正在分析您的意图...",
                "metadata": {"progress": 10, "phase": "intent"},
            })

            try:
                # 执行编排工作流
                result = await _workflow.run(
                    session_id=session_id,
                    user_id=user_id,
                    user_input=user_input,
                )

                # 推送最终响应
                await websocket.send_json({
                    "type": "agent_response",
                    "session_id": session_id,
                    "content": result["final_response"],
                    "metadata": {
                        "phase": result["phase"],
                        "intent": result.get("intent_analysis", {}),
                    },
                })

            except Exception as e:
                logger.exception(f"工作流执行失败: {e}")
                await websocket.send_json({
                    "type": "error",
                    "session_id": session_id,
                    "content": f"处理过程中出现错误: {str(e)}",
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket 断开: user_id={user_id}")
    except Exception as e:
        logger.exception(f"WebSocket 异常: {e}")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
