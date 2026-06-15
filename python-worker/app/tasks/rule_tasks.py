"""规则引擎 Celery 任务"""
import json
import logging
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(queue="rule_engine")
def evaluate_order_rules(order_id: int):
    """对订单执行匹配规则"""
    logger.info(f"评估订单 {order_id} 的规则...")
    # TODO: 查询订单信息
    # TODO: 查询所有启用的规则
    # TODO: 按优先级匹配条件
    # TODO: 执行匹配的动作
    return {"order_id": order_id, "matched_rules": 0}


@celery_app.task(queue="rule_engine")
def check_stock_alerts():
    """检查库存预警"""
    logger.info("检查库存预警...")
    # TODO: 查询 stock <= stock_warning_threshold 的商品
    # TODO: 发送通知（钉钉/企微/邮件）
    return "checked"


def match_condition(order_data: dict, condition: dict) -> bool:
    """匹配单个条件"""
    field = condition.get("field", "")
    operator = condition.get("operator", "eq")
    value = condition.get("value")

    # 获取字段值
    keys = field.split(".")
    current = order_data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return False

    # 防御：null 值导致后续比较操作 crash
    if current is None:
        return False

    if operator == "eq":
        return current == value
    elif operator == "neq":
        return current != value
    elif operator == "gt":
        try:
            return current > value
        except (TypeError, ValueError):
            return False
    elif operator == "gte":
        try:
            return current >= value
        except (TypeError, ValueError):
            return False
    elif operator == "lt":
        try:
            return current < value
        except (TypeError, ValueError):
            return False
    elif operator == "lte":
        try:
            return current <= value
        except (TypeError, ValueError):
            return False
    elif operator == "in":
        try:
            return current in value
        except TypeError:
            return False
    elif operator == "not_in":
        try:
            return current not in value
        except TypeError:
            return False
    elif operator == "contains":
        try:
            return value in str(current)
        except (TypeError, ValueError):
            return False
    return False


def evaluate_conditions(order_data: dict, conditions: dict) -> bool:
    """评估条件组合（支持 AND/OR）"""
    logic = conditions.get("logic", "AND")
    cond_list = conditions.get("conditions", [])

    if not cond_list:
        return False

    if logic == "AND":
        return all(match_condition(order_data, c) for c in cond_list)
    elif logic == "OR":
        return any(match_condition(order_data, c) for c in cond_list)
    return False
