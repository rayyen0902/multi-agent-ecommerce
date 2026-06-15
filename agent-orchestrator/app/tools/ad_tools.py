"""广告投放工具集（新增功能 - 骨架实现）"""
from langchain_core.tools import tool


def create_ad_tools() -> list:
    """创建广告投放相关工具集

    注意: 广告投放功能需要对接各平台广告API（淘宝直通车、京东快车、拼多多推广），
    目前为骨架实现，实际使用时需补充平台广告SDK集成。
    """

    @tool
    async def create_ad_campaign(
        platform: str,
        campaign_name: str,
        daily_budget: float,
        product_ids: list[str],
        keywords: list[str] = None,
    ) -> dict:
        """创建广告投放计划。
        platform: 平台(taobao/jd/pdd)
        campaign_name: 计划名称
        daily_budget: 日预算(元)
        product_ids: 推广商品ID列表
        keywords: 关键词列表(可选)

        注意: 此操作涉及真实费用支出，创建前请确认用户授权。
        """
        # TODO: 对接实际广告平台 API
        return {
            "status": "mock_created",
            "campaign_id": "MOCK_CAMPAIGN_001",
            "platform": platform,
            "campaign_name": campaign_name,
            "daily_budget": daily_budget,
            "message": "广告计划已创建（模拟）。实际使用需对接平台广告API。",
        }

    @tool
    async def get_ad_performance(
        platform: str,
        campaign_id: str = "",
        date_from: str = "",
        date_to: str = "",
    ) -> dict:
        """查询广告投放效果数据。
        platform: 平台(taobao/jd/pdd)
        campaign_id: 计划ID(可选，不传则查全部)
        date_from/date_to: 日期范围(YYYY-MM-DD)

        返回: 展现量、点击量、花费、ROI、转化率等指标。
        """
        # TODO: 对接实际广告平台 API
        return {
            "status": "mock_data",
            "platform": platform,
            "campaign_id": campaign_id,
            "metrics": {
                "impressions": 0,
                "clicks": 0,
                "cost": 0.0,
                "roi": 0.0,
                "conversion_rate": 0.0,
            },
            "message": "广告数据（模拟）。实际使用需对接平台广告API。",
        }

    @tool
    async def adjust_ad_budget(
        platform: str,
        campaign_id: str,
        new_daily_budget: float,
    ) -> dict:
        """调整广告计划的日预算。
        platform: 平台(taobao/jd/pdd)
        campaign_id: 计划ID
        new_daily_budget: 新的日预算(元)

        注意: 建议预算调整幅度不超过当前的30%。
        """
        # TODO: 对接实际广告平台 API
        return {
            "status": "mock_adjusted",
            "campaign_id": campaign_id,
            "new_daily_budget": new_daily_budget,
            "message": "预算已调整（模拟）。实际使用需对接平台广告API。",
        }

    return [create_ad_campaign, get_ad_performance, adjust_ad_budget]
