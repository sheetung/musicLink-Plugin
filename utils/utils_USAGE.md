# Utils 工具模块使用指南

DataCardPlugin 的 `utils` 模块提供了两大功能：**音乐卡片发送** 和 **合并转发消息**。本文档详细介绍这两个功能的使用方法。

---

# 📀 音乐卡片功能

## 概述

`music_card.py` 提供了通过 NapCat HTTP API 发送 QQ 音乐卡片的功能，支持自定义音乐卡片和平台音乐卡片。

## 主要功能

### 1. MusicCardSender 类

主要的音乐卡片发送器类。

#### 初始化

```python
from utils.music_card import MusicCardSender

sender = MusicCardSender(
    http_url="http://127.0.0.1:3000",  # NapCat HTTP API地址
    access_token=None  # 可选的访问令牌
)
```

#### 发送自定义音乐卡片

```python
result = await sender.send_custom_music_card(
    target_id=123456789,      # 目标ID（群号或用户ID）
    target_type="group",      # 目标类型 ('group' 或 'private')
    title="歌曲名称",          # 音乐标题
    audio_url="https://example.com/music.mp3",  # 音乐文件直链
    jump_url="https://example.com/song",        # 点击卡片跳转链接
    image_url="https://example.com/cover.jpg",  # 封面图片URL（可选）
    content="歌手名 - 专辑名"  # 音乐描述（可选）
)
```

**参数说明**:
- `target_id`: 目标群号或用户QQ号
- `target_type`: `"group"` 表示群聊，`"private"` 表示私聊
- `title`: 音乐卡片显示的标题
- `audio_url`: 音乐文件的直链地址（必须是可直接播放的音频 URL）
- `jump_url`: 用户点击卡片时跳转的链接
- `image_url`: 音乐封面图片 URL（可选）
- `content`: 音乐描述信息（可选）

**返回值**:
```python
{
    "success": True,     # 是否成功
    "data": {...}        # API 响应数据
}
```

#### 发送平台音乐卡片

```python
result = await sender.send_platform_music_card(
    target_id=123456789,      # 目标ID
    target_type="group",      # 目标类型
    platform="qq",            # 平台类型 ('qq', '163', 'xm')
    music_id="001ABC123"      # 平台音乐ID
)
```

**支持的平台**:
- `"qq"`: QQ音乐
- `"163"`: 网易云音乐
- `"xm"`: 虾米音乐

**参数说明**:
- `platform`: 音乐平台标识
- `music_id`: 在该平台的音乐ID（可以在平台分享链接中找到）

### 2. 便捷函数

#### send_music_card

快速发送自定义音乐卡片的便捷函数：

```python
from utils import send_music_card

result = await send_music_card(
    target_id=123456789,
    target_type="group",
    title="夜曲",
    audio_url="https://example.com/music.mp3",
    jump_url="https://example.com/song",
    image_url="https://example.com/cover.jpg",
    content="周杰伦 - 十一月的萧邦",
    http_url="http://127.0.0.1:3000"
)
```

### 3. 配置更新

可以在运行时更新配置：

```python
sender.update_config(
    http_url="http://192.168.1.100:3000",
    access_token="your_token_here"
)
```

## 使用示例

### 示例 1: 在 default.py 中发送音乐卡片

```python
from utils import MusicCardSender

# 在 DefaultEventListener 的 __init__ 方法中初始化
def __init__(self):
    super().__init__()
    self.music_sender = MusicCardSender(http_url="http://127.0.0.1:3000")

# 在事件处理器中使用
@self.handler(events.GroupMessageReceived)
async def handler(event_context: context.EventContext):
    message_text = str(event_context.event.message_chain)

    if message_text.startswith("点歌 "):
        song_name = message_text[3:].strip()

        # 这里可以调用音乐API获取歌曲信息
        # 示例：假设已经获取到歌曲信息
        result = await self.music_sender.send_custom_music_card(
            target_id=event_context.event.launcher_id,
            target_type="group",
            title=song_name,
            audio_url="https://example.com/music.mp3",
            jump_url="https://example.com/song",
            image_url="https://example.com/cover.jpg",
            content="歌手名 - 专辑名"
        )

        if result['success']:
            print(f"音乐卡片发送成功: {song_name}")
        else:
            await event_context.reply(
                platform_message.MessageChain([
                    platform_message.Plain(text=f"发送失败: {result['error']}")
                ])
            )
```

### 示例 2: 发送平台音乐

```python
# QQ音乐
await sender.send_platform_music_card(
    target_id=123456789,
    target_type="group",
    platform="qq",
    music_id="001ABC123"
)

# 网易云音乐
await sender.send_platform_music_card(
    target_id=123456789,
    target_type="group",
    platform="163",
    music_id="12345678"
)
```

### 示例 3: 私聊发送音乐

```python
result = await sender.send_custom_music_card(
    target_id=987654321,      # 用户QQ号
    target_type="private",    # 私聊
    title="夜曲",
    audio_url="https://example.com/music.mp3",
    jump_url="https://example.com/song"
)
```

## 错误处理

```python
result = await sender.send_custom_music_card(...)

if result['success']:
    print("音乐卡片发送成功")
    print(f"响应数据: {result['data']}")
else:
    print(f"发送失败: {result['error']}")
    if 'data' in result:
        print(f"详细信息: {result['data']}")
```

## 注意事项

1. **音频 URL**: `audio_url` 必须是可直接播放的音频文件链接（如 .mp3, .flac 等）
2. **API 地址**: 确保 NapCat HTTP API 正在运行且地址正确
3. **权限**: 确保机器人在目标群或用户有发送消息的权限
4. **平台 ID**: 发送平台音乐时，需要正确的音乐 ID

---

# 📨 合并转发功能

## 概述

`forward_message.py` 提供了完整的合并转发消息功能，支持通过 OneBot v11 协议发送合并转发消息。

## 主要功能

### 1. ForwardMessageSender 类

主要的合并转发消息发送器类。

#### 初始化

```python
from utils.forward_message import ForwardMessageSender

sender = ForwardMessageSender(
    http_url="http://127.0.0.1:3000",  # OneBot v11 API地址
    access_token=None  # 可选的访问令牌
)
```

#### 发送合并转发消息

```python
result = await sender.send_forward(
    group_id=123456789,  # 目标群号
    messages=[
        {
            "content": [
                {"type": "text", "data": {"text": "第一条消息"}},
                {"type": "image", "data": {"file": "https://example.com/image.jpg"}}
            ]
        },
        {
            "content": [
                {"type": "text", "data": {"text": "第二条消息"}}
            ]
        }
    ],
    prompt="聊天记录",  # 转发卡片标题
    summary="查看消息",  # 转发卡片摘要
    source="聊天记录",  # 转发来源
    user_id="10000",  # 虚拟发送者QQ号
    nickname="消息助手",  # 虚拟发送者昵称
    mode="multi"  # "multi"=多节点模式, "single"=单节点模式
)
```

**参数说明**:
- `group_id`: 目标群号
- `messages`: 消息列表，每个消息包含 `content` 字段
- `prompt`: 转发卡片标题（显示在聊天列表）
- `summary`: 转发卡片摘要（显示在聊天列表下方）
- `source`: 转发来源
- `user_id`: 虚拟发送者的 QQ 号
- `nickname`: 虚拟发送者的昵称
- `mode`: 消息模式
  - `"multi"`: 多节点模式，每条消息作为独立节点（默认）
  - `"single"`: 单节点模式，所有消息合并到一个节点

### 2. convert_to_forward 方法

将原始消息文本转换为合并转发格式。支持使用特殊分隔符分割多条消息。

#### 使用方法

```python
sender = ForwardMessageSender()

# 使用默认分隔符 '\n---\n'
messages = sender.convert_to_forward("""
第一条消息
---
![图片](https://example.com/image.jpg)
第二条消息的文本
---
第三条消息
""")

# 使用自定义分隔符
messages = sender.convert_to_forward(
    "消息1|||消息2|||消息3",
    separator="|||"
)
```

#### 输出格式

```python
[
    {"content": [{"type": "text", "data": {"text": "第一条消息"}}]},
    {
        "content": [
            {"type": "image", "data": {"file": "https://example.com/image.jpg"}},
            {"type": "text", "data": {"text": "第二条消息的文本"}}
        ]
    },
    {"content": [{"type": "text", "data": {"text": "第三条消息"}}]}
]
```

### 3. 便捷函数

#### send_forward_message

快速发送合并转发消息的便捷函数。

```python
from utils import send_forward_message

result = await send_forward_message(
    group_id=123456789,
    messages=messages,
    prompt="流量卡查询结果",
    summary="查看详情",
    mode="multi",
    http_url="http://127.0.0.1:3000"
)
```

#### convert_message_to_forward

快速转换消息格式的便捷函数。

```python
from utils import convert_message_to_forward

messages = convert_message_to_forward(
    "消息1\n---\n消息2\n---\n消息3"
)
```

## 使用示例

### 示例 1: 基本集成

```python
from utils import ForwardMessageSender

# 在事件处理器中
@self.handler(events.GroupMessageReceived)
async def handler(event_context: context.EventContext):
    # ... 获取流量卡查询结果 ...

    # 将结果转换为合并转发格式
    response_text = '\n'.join(reply_content)

    # 使用 \n---\n 作为分隔符
    forward_sender = ForwardMessageSender(http_url="http://127.0.0.1:3000")
    messages = forward_sender.convert_to_forward(response_text)

    # 发送合并转发消息
    result = await forward_sender.send_forward(
        group_id=event_context.event.launcher_id,
        messages=messages,
        prompt="流量卡查询结果",
        summary="查看详情",
        nickname="流量卡助手",
        mode="multi"
    )

    if result['success']:
        print("合并转发发送成功")
    else:
        print(f"发送失败: {result['error']}")
```

### 示例 2: 高级集成（混合普通消息和合并转发）

```python
# 检查消息文本，如果包含特殊标识符则使用合并转发
message_text = str(event_context.event.message_chain)

if '流量卡' in message_text:
    # ... 查询流量卡 ...

    # 判断结果数量，如果超过3个则使用合并转发
    if len(result['results']) > 3:
        # 构建合并转发消息
        forward_messages = []
        for product in result['results']:
            content_text = f"""产品名称: {product['产品名称']}
通用流量: {product['通用流量']}
定向流量: {product['定向流量']}
通话时长: {product['通话时长']}
适用年龄: {product['适用年龄']}
详情链接: {product['详情链接']}"""

            forward_messages.append({
                "content": [
                    {"type": "text", "data": {"text": content_text}}
                ]
            })

        # 发送合并转发
        forward_sender = ForwardMessageSender()
        await forward_sender.send_forward(
            group_id=event_context.event.launcher_id,
            messages=forward_messages,
            prompt=f"流量卡查询结果 - {keyword}",
            summary=f"共{len(result['results'])}个产品",
            nickname="流量卡助手",
            mode="multi"
        )
    else:
        # 普通消息发送（原有逻辑）
        await event_context.reply(
            platform_message.MessageChain(message_chain)
        )
```

## 消息分隔符说明

### 默认分隔符: `\n---\n`

这是最常用的分隔符，在构建回复内容时使用：

```python
reply_content = []
reply_content.append("第一条消息")
reply_content.append("---")  # 分隔符
reply_content.append("第二条消息")
reply_content.append("---")  # 分隔符
reply_content.append("第三条消息")

response_text = '\n'.join(reply_content)  # 自动转换为 \n---\n
messages = convert_message_to_forward(response_text)
```

### 自定义分隔符

你可以使用任何自定义分隔符：

```python
# 使用 |||| 作为分隔符
messages = convert_message_to_forward(
    "消息1||||消息2||||消息3",
    separator="||||"
)

# 使用 [SPLIT] 作为分隔符
messages = convert_message_to_forward(
    "消息1[SPLIT]消息2[SPLIT]消息3",
    separator="[SPLIT]"
)
```

## 消息模式说明

### Multi 模式（默认）

每条消息作为独立的节点显示，用户打开合并转发后会看到多条分开的消息。

**适用场景**：
- 多个产品信息
- 多条独立的消息记录

### Single 模式

所有消息内容合并到一个节点内显示。

**适用场景**：
- 长文本分段显示
- 需要保持内容连贯性

```python
# 使用 single 模式
result = await sender.send_forward(
    group_id=123456789,
    messages=messages,
    mode="single"  # 单节点模式
)
```

## 图片支持

支持 markdown 格式的图片，格式为 `![描述](图片URL)`：

```python
message_with_image = """
这是文本内容
![产品图片](https://example.com/product.jpg)
这是图片后的文本
"""

messages = convert_message_to_forward(message_with_image)
```

转换后会自动识别图片并转换为正确的格式：

```python
{
    "content": [
        {"type": "text", "data": {"text": "这是文本内容"}},
        {"type": "image", "data": {"file": "https://example.com/product.jpg"}},
        {"type": "text", "data": {"text": "这是图片后的文本"}}
    ]
}
```

## 错误处理

```python
result = await sender.send_forward(...)

if result['success']:
    print("发送成功")
    print(f"响应数据: {result['data']}")
else:
    print(f"发送失败: {result['error']}")
    if 'data' in result:
        print(f"详细信息: {result['data']}")
```

## 配置更新

可以在运行时更新配置：

```python
sender.update_config(
    http_url="http://192.168.1.100:3000",
    access_token="your_token_here"
)
```

## 注意事项

### 音乐卡片

1. **音频 URL**: 必须是可直接播放的音频文件链接
2. **NapCat API**: 确保 NapCat HTTP API 正在运行
3. **网络配置**: 确保 API 地址和端口正确
4. **权限**: 确保机器人有发送消息的权限

### 合并转发

1. **OneBot v11 API**: 确保你的 OneBot 实现（如 NapCat、go-cqhttp 等）支持 `send_forward_msg` 接口
2. **网络配置**: 确保 API 地址和端口正确
3. **消息长度**: 避免单条消息过长，建议使用分隔符拆分
4. **图片 URL**: 图片 URL 必须是可访问的 HTTP/HTTPS 地址或本地文件路径
5. **群权限**: 确保机器人在目标群有发送消息的权限

---

## 完整示例

### 同时使用音乐卡片和合并转发

```python
from utils import MusicCardSender, ForwardMessageSender

class DefaultEventListener(EventListener):

    def __init__(self):
        super().__init__()
        # 初始化音乐卡片发送器
        self.music_sender = MusicCardSender(http_url="http://127.0.0.1:3000")
        # 初始化合并转发发送器
        self.forward_sender = ForwardMessageSender(http_url="http://127.0.0.1:3000")

    async def initialize(self):
        await super().initialize()

        @self.handler(events.GroupMessageReceived)
        async def handler(event_context: context.EventContext):
            message_text = str(event_context.event.message_chain)

            # 点歌功能
            if message_text.startswith("点歌 "):
                song_name = message_text[3:].strip()
                result = await self.music_sender.send_custom_music_card(
                    target_id=event_context.event.launcher_id,
                    target_type="group",
                    title=song_name,
                    audio_url="https://example.com/music.mp3",
                    jump_url="https://example.com/song"
                )

            # 流量卡查询 - 使用合并转发
            elif message_text.startswith("流量卡"):
                # ... 查询逻辑 ...
                if len(results) > 3:
                    response_text = '\n---\n'.join([str(r) for r in results])
                    messages = self.forward_sender.convert_to_forward(response_text)
                    result = await self.forward_sender.send_forward(
                        group_id=event_context.event.launcher_id,
                        messages=messages,
                        prompt="流量卡查询结果",
                        summary=f"找到 {len(results)} 个结果"
                    )
```

## 更多示例

查看以下文件获取更多示例：
- **合并转发**: `examples/forward_example.py`
- **测试脚本**: `examples/test_forward.py`

---

## 快速参考

### 导入方式

```python
# 音乐卡片
from utils import MusicCardSender, send_music_card

# 合并转发
from utils import ForwardMessageSender, send_forward_message, convert_message_to_forward

# 或者全部导入
from utils import (
    MusicCardSender,
    send_music_card,
    ForwardMessageSender,
    send_forward_message,
    convert_message_to_forward
)
```

### API 快速对照表

| 功能 | 类 | 主要方法 | 便捷函数 |
|------|-----|----------|----------|
| 自定义音乐 | `MusicCardSender` | `send_custom_music_card()` | `send_music_card()` |
| 平台音乐 | `MusicCardSender` | `send_platform_music_card()` | - |
| 合并转发 | `ForwardMessageSender` | `send_forward()` | `send_forward_message()` |
| 消息转换 | `ForwardMessageSender` | `convert_to_forward()` | `convert_message_to_forward()` |

---

**版本**: 1.0.0
**最后更新**: 2025-12-07
