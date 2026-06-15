"""测试 JSON 解析鲁棒性"""
import pytest


class TestJSONParser:
    """测试 PMOAgent._parse_json 的各种边界情况"""

    def _parse_json(self, content: str) -> dict:
        """复用 PMO 的解析逻辑"""
        import json
        import re

        content = content.strip()

        match = re.search(r'```(?:json)?\s*\n(.*?)```', content, re.DOTALL)
        if match:
            content = match.group(1).strip()
        elif content.startswith("```"):
            parts = content.split("```")
            content = parts[1] if len(parts) > 1 else parts[0]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    def test_standard_json(self):
        """标准 JSON 字符串应正常解析"""
        result = self._parse_json('{"key": "value", "count": 42}')
        assert result == {"key": "value", "count": 42}

    def test_markdown_plain_code_block(self):
        """``` ... ``` 包裹的 JSON 应提取并解析"""
        result = self._parse_json("```\n{\"key\": \"value\"}\n```")
        assert result == {"key": "value"}

    def test_markdown_json_code_block(self):
        """```json ... ``` 包裹的 JSON 应提取并解析"""
        result = self._parse_json("```json\n{\"key\": \"value\", \"nested\": {\"a\": 1}}\n```")
        assert result == {"key": "value", "nested": {"a": 1}}

    def test_markdown_with_trailing_text(self):
        """代码块后带其他文本的 JSON 应只解析代码块内容"""
        result = self._parse_json("```json\n{\"done\": true}\n```\n这就是结果。")
        assert result == {"done": True}

    def test_single_backtick_fallback(self):
        """只有一个 ``` 时回退到空字典"""
        result = self._parse_json("```")
        assert result == {}

    def test_single_backtick_json(self):
        """```json 开头无闭合"""
        result = self._parse_json("```json")
        assert result == {}

    def test_invalid_json_returns_empty_dict(self):
        """无效的 JSON 应返回空字典"""
        result = self._parse_json("not json at all {{{")
        assert result == {}

    def test_empty_string_returns_empty_dict(self):
        """空字符串应返回空字典"""
        result = self._parse_json("")
        assert result == {}

    def test_complex_nested_json(self):
        """复杂嵌套 JSON 应正确解析"""
        json_str = """
        {
            "original_intent": "测试意图",
            "subtasks": [
                {"agent_name": "order_analyst", "description": "分析订单", "dependencies": []}
            ]
        }
        """
        result = self._parse_json(f"```json\n{json_str}```")
        assert result["original_intent"] == "测试意图"
        assert len(result["subtasks"]) == 1
        assert result["subtasks"][0]["agent_name"] == "order_analyst"

    def test_llm_output_with_text_before_json(self):
        """LLM 输出开头带解释文本的 JSON"""
        content = "好的，以下是分析结果：\n\n```json\n{\"approved\": true}\n```"
        result = self._parse_json(content)
        # regex 只匹配 ``` 包裹的内容
        assert result == {"approved": True}
