"""
合并转发消息工具模块
支持通过OneBot v11协议发送合并转发消息
支持多种模式：单节点模式和多节点模式
"""

import json
import re
import aiohttp
import os
from typing import List, Dict, Optional


class ForwardMessageSender:
    """合并转发消息发送器"""

    def __init__(self, http_url: str = "http://127.0.0.1:3000", access_token: Optional[str] = None):
        """
        初始化合并转发消息发送器

        Args:
            http_url: OneBot v11 HTTP API地址，默认为 http://127.0.0.1:3000
            access_token: 访问令牌（如果配置了的话）
        """
        self.http_url = http_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json"
        }
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

    async def send_forward(
        self,
        group_id: int,
        messages: List[Dict],
        prompt: str = "聊天记录",
        summary: str = "查看消息",
        source: str = "聊天记录",
        user_id: str = "10000",
        nickname: str = "消息助手",
        mode: str = "multi"
    ) -> Dict[str, any]:
        """
        发送合并转发消息

        Args:
            group_id: 目标群号
            messages: 消息列表，每个消息包含content字段
            prompt: 转发卡片标题（显示在聊天列表）
            summary: 转发卡片摘要（显示在聊天列表下方）
            source: 转发来源
            user_id: 发送者QQ号（虚拟）
            nickname: 发送者昵称（虚拟）
            mode: 消息模式
                - "single": 单节点模式，所有消息合并到一个节点内
                - "multi": 多节点模式，每条消息作为独立节点（默认）

        Returns:
            API响应结果
        """
        # 构建消息节点
        if mode == "single":
            nodes = self._build_single_node(messages, user_id, nickname)
            item_count = len(nodes[0]['data']['content']) if nodes else 0
        else:
            nodes = self._build_nodes(messages, user_id, nickname)
            item_count = len(nodes)

        # 自动追加统计信息到摘要
        formatted_summary = f"{summary} | 共{item_count}条内容"

        # 构建请求数据
        message_data = {
            "group_id": group_id,
            "messages": nodes,
            "prompt": prompt,
            "summary": formatted_summary,
            "source": source
        }

        # 发送HTTP请求
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.http_url}/send_forward_msg",
                    json=message_data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return {
                            "success": True,
                            "data": result
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "data": result
                        }
            except aiohttp.ClientError as e:
                return {
                    "success": False,
                    "error": str(e)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }

    def _build_single_node(self, messages: List[Dict], user_id: str, nickname: str) -> List[Dict]:
        """
        构建单节点消息（所有内容合并到一个节点）

        Args:
            messages: 消息列表
            user_id: 用户ID
            nickname: 用户昵称

        Returns:
            单节点消息列表
        """
        return [{
            "type": "node",
            "data": {
                "user_id": user_id,
                "nickname": nickname,
                "content": self._parse_contents(messages)
            }
        }]

    def _build_nodes(self, messages: List[Dict], user_id: str, nickname: str) -> List[Dict]:
        """
        构建多节点消息（每条消息作为独立节点）

        Args:
            messages: 消息列表
            user_id: 用户ID
            nickname: 用户昵称

        Returns:
            多节点消息列表
        """
        nodes = []
        for msg in messages:
            node = {
                "type": "node",
                "data": {
                    "user_id": user_id,
                    "nickname": nickname,
                    "content": self._parse_content(msg)
                }
            }
            nodes.append(node)
        return nodes

    def _parse_contents(self, messages: List[Dict]) -> List[Dict]:
        """
        解析全部消息内容（用于单节点模式）

        Args:
            messages: 消息列表

        Returns:
            合并后的消息内容
        """
        contents = []
        for msg in messages:
            contents.extend(self._parse_content(msg))
        return contents

    def _parse_content(self, msg: Dict) -> List[Dict]:
        """
        解析单条消息内容

        Args:
            msg: 消息字典，必须包含content字段

        Returns:
            消息内容列表
        """
        return msg.get("content", [])

    def _get_media_path(self, path: str) -> str:
        """
        获取合法媒体路径

        Args:
            path: 原始路径

        Returns:
            格式化后的路径
        """
        if path.startswith(('http://', 'https://')):
            return path
        if os.path.isfile(path):
            return f"file:///{os.path.abspath(path)}"
        return ""

    def convert_to_forward(self, raw_message: str, separator: str = '\n---\n') -> List[Dict]:
        """
        将原始消息文本转换为合并转发格式
        支持自定义分隔符分割多条消息

        Args:
            raw_message: 原始消息文本
            separator: 消息分隔符，默认为 '\n---\n'

        Returns:
            转换后的消息列表，每个元素包含content字段

        示例:
            输入:
            "消息1\n---\n![图片](url)\n消息2\n---\n消息3"

            输出:
            [
                {"content": [{"type": "text", "data": {"text": "消息1"}}]},
                {"content": [
                    {"type": "image", "data": {"file": "url"}},
                    {"type": "text", "data": {"text": "消息2"}}
                ]},
                {"content": [{"type": "text", "data": {"text": "消息3"}}]}
            ]
        """
        messages = []

        for block in raw_message.split(separator):
            block = block.strip()
            if not block:
                continue

            content = []
            # 使用正则表达式分割文本和图片
            elements = re.split(r'(!\[.*?\]\(.*?\))', block)

            for elem in elements:
                elem = elem.strip()
                if not elem:
                    continue

                if elem.startswith('!['):  # 图片
                    match = re.match(r'!\[.*?\]\((.*?)\)', elem)
                    if match:
                        content.append({
                            "type": "image",
                            "data": {"file": match.group(1)}
                        })
                else:  # 文本
                    content.append({
                        "type": "text",
                        "data": {"text": elem}
                    })

            if content:
                messages.append({"content": content})

        return messages

    def update_config(self, http_url: Optional[str] = None, access_token: Optional[str] = None):
        """
        更新配置

        Args:
            http_url: 新的HTTP API地址
            access_token: 新的访问令牌
        """
        if http_url:
            self.http_url = http_url.rstrip('/')
        if access_token is not None:
            self.access_token = access_token
            if access_token:
                self.headers["Authorization"] = f"Bearer {access_token}"
            elif "Authorization" in self.headers:
                del self.headers["Authorization"]


# 便捷函数
async def send_forward_message(
    group_id: int,
    messages: List[Dict],
    prompt: str = "聊天记录",
    summary: str = "查看消息",
    source: str = "聊天记录",
    user_id: str = "10000",
    nickname: str = "消息助手",
    mode: str = "multi",
    http_url: str = "http://127.0.0.1:3000",
    access_token: Optional[str] = None
) -> Dict[str, any]:
    """
    快速发送合并转发消息的便捷函数

    Args:
        group_id: 目标群号
        messages: 消息列表
        prompt: 转发卡片标题
        summary: 转发卡片摘要
        source: 转发来源
        user_id: 发送者QQ号
        nickname: 发送者昵称
        mode: 消息模式（single/multi）
        http_url: OneBot v11 HTTP API地址
        access_token: 访问令牌

    Returns:
        发送结果
    """
    sender = ForwardMessageSender(http_url, access_token)
    return await sender.send_forward(
        group_id=group_id,
        messages=messages,
        prompt=prompt,
        summary=summary,
        source=source,
        user_id=user_id,
        nickname=nickname,
        mode=mode
    )


def convert_message_to_forward(raw_message: str, separator: str = '\n---\n') -> List[Dict]:
    """
    将原始消息转换为合并转发格式的便捷函数

    Args:
        raw_message: 原始消息文本
        separator: 消息分隔符

    Returns:
        转换后的消息列表
    """
    sender = ForwardMessageSender()
    return sender.convert_to_forward(raw_message, separator)
