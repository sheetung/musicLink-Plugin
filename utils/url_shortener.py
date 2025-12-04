"""
短链接服务模块
支持多种短链接API服务
"""

import aiohttp
from typing import Optional, Dict, Any


class URLShortener:
    """短链接服务"""

    def __init__(self):
        """初始化短链接服务"""
        # 可用的短链接服务列表，按优先级排序
        self.services = [
            {
                'name': 'tinyurl',
                'url': 'http://tinyurl.com/api-create.php',
                'method': 'get',
                'params': lambda long_url: {'url': long_url}
            },
            {
                'name': 'is.gd',
                'url': 'https://is.gd/create.php',
                'method': 'post',
                'data': lambda long_url: {'format': 'simple', 'url': long_url}
            },
            {
                'name': 'v.gd',
                'url': 'https://v.gd/create.php',
                'method': 'post',
                'data': lambda long_url: {'format': 'simple', 'url': long_url}
            }
        ]

    async def shorten_url(self, long_url: str) -> str:
        """
        将长链接转换为短链接

        Args:
            long_url: 需要缩短的长链接

        Returns:
            缩短后的链接，如果失败则返回原链接
        """
        if not long_url or not long_url.strip():
            return long_url

        # 如果链接已经很短（少于50个字符），直接返回
        if len(long_url) < 50:
            return long_url

        # 尝试多个短链接服务
        for service in self.services:
            try:
                short_url = await self._try_service(service, long_url)
                if short_url and short_url != long_url:
                    return short_url
            except Exception as e:
                print(f"短链接服务 {service['name']} 失败: {str(e)}")
                continue

        # 如果所有服务都失败，返回原链接
        return long_url

    async def _try_service(self, service: Dict[str, Any], long_url: str) -> Optional[str]:
        """
        尝试使用指定的短链接服务

        Args:
            service: 服务配置
            long_url: 长链接

        Returns:
            短链接或None
        """
        async with aiohttp.ClientSession() as session:
            try:
                if service['method'] == 'get':
                    params = service['params'](long_url)
                    async with session.get(
                        service['url'],
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            result = await response.text()
                            return result.strip()
                else:  # POST
                    data = service['data'](long_url)
                    async with session.post(
                        service['url'],
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            result = await response.text()
                            return result.strip()
            except Exception as e:
                raise e

        return None

    async def shorten_multiple_urls(self, urls: Dict[str, str]) -> Dict[str, str]:
        """
        批量缩短多个URL

        Args:
            urls: 键值对，键为标识，值为长链接

        Returns:
            缩短后的URL字典
        """
        result = {}
        for key, url in urls.items():
            result[key] = await self.shorten_url(url)
        return result


# 全局短链接服务实例
_url_shortener = URLShortener()


async def shorten_url(long_url: str) -> str:
    """
    便捷函数：缩短单个URL

    Args:
        long_url: 长链接

    Returns:
        短链接
    """
    return await _url_shortener.shorten_url(long_url)


async def shorten_urls(urls: Dict[str, str]) -> Dict[str, str]:
    """
    便捷函数：批量缩短URL

    Args:
        urls: URL字典

    Returns:
        短链接字典
    """
    return await _url_shortener.shorten_multiple_urls(urls)