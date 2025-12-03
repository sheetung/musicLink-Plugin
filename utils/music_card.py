"""
音乐卡片发送工具模块
支持通过NapCat HTTP API发送QQ音乐卡片
"""

import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any


class MusicCardSender:
    """音乐卡片发送器"""

    def __init__(self, http_url: str = "http://127.0.0.1:3000", access_token: Optional[str] = None):
        """
        初始化音乐卡片发送器

        Args:
            http_url: NapCat HTTP API地址，默认为 http://127.0.0.1:3000
            access_token: 访问令牌（如果配置了的话）
        """
        self.http_url = http_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json"
        }
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

    async def send_custom_music_card(
        self,
        target_id: int,
        target_type: str,
        title: str,
        audio_url: str,
        jump_url: str,
        image_url: Optional[str] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送自定义音乐卡片

        Args:
            target_id: 目标ID（群号或用户ID）
            target_type: 目标类型 ('group' 或 'private')
            title: 音乐标题
            audio_url: 音乐文件直链
            jump_url: 点击卡片跳转链接
            image_url: 封面图片URL（可选）
            content: 音乐描述（可选）

        Returns:
            API响应结果
        """

        # 构建音乐卡片消息段
        music_segment = {
            "type": "music",
            "data": {
                "type": "custom",
                "url": jump_url,
                "audio": audio_url,
                "title": title
            }
        }

        # 添加可选参数
        if content:
            music_segment["data"]["content"] = content
        if image_url:
            music_segment["data"]["image"] = image_url

        # 构建消息体
        message = [music_segment]

        # 根据目标类型选择API端点
        if target_type == "group":
            endpoint = f"{self.http_url}/send_group_msg"
            data = {
                "group_id": target_id,
                "message": message
            }
        else:  # private
            endpoint = f"{self.http_url}/send_private_msg"
            data = {
                "user_id": target_id,
                "message": message
            }

        # 发送HTTP请求
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    endpoint,
                    json=data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
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

    async def send_platform_music_card(
        self,
        target_id: int,
        target_type: str,
        platform: str,
        music_id: str
    ) -> Dict[str, Any]:
        """
        发送平台音乐卡片（QQ音乐、网易云音乐等）

        Args:
            target_id: 目标ID（群号或用户ID）
            target_type: 目标类型 ('group' 或 'private')
            platform: 平台类型 ('qq', '163', 'xm')
            music_id: 平台音乐ID

        Returns:
            API响应结果
        """

        # 构建音乐卡片消息段
        music_segment = {
            "type": "music",
            "data": {
                "type": platform,
                "id": music_id
            }
        }

        # 构建消息体
        message = [music_segment]

        # 根据目标类型选择API端点
        if target_type == "group":
            endpoint = f"{self.http_url}/send_group_msg"
            data = {
                "group_id": target_id,
                "message": message
            }
        else:  # private
            endpoint = f"{self.http_url}/send_private_msg"
            data = {
                "user_id": target_id,
                "message": message
            }

        # 发送HTTP请求
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    endpoint,
                    json=data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
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
async def send_music_card(
    target_id: int,
    target_type: str,
    title: str,
    audio_url: str,
    jump_url: str,
    image_url: Optional[str] = None,
    content: Optional[str] = None,
    http_url: str = "http://127.0.0.1:3000",
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    快速发送音乐卡片的便捷函数

    Args:
        target_id: 目标ID
        target_type: 目标类型
        title: 音乐标题
        audio_url: 音乐文件URL
        jump_url: 跳转链接
        image_url: 封面图片URL
        content: 音乐描述
        http_url: NapCat HTTP API地址
        access_token: 访问令牌

    Returns:
        发送结果
    """
    sender = MusicCardSender(http_url, access_token)
    return await sender.send_custom_music_card(
        target_id=target_id,
        target_type=target_type,
        title=title,
        audio_url=audio_url,
        jump_url=jump_url,
        image_url=image_url,
        content=content
    )