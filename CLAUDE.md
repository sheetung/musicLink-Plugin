# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a music search and download plugin for LangBot, a chatbot framework. The plugin allows users to search for songs and retrieve high-quality music download links through chat commands.

## Architecture

### Plugin Structure
- **Entry Point**: `main.py:7` - Contains the `musicLink` class which extends `BasePlugin`
- **Event Listener**: `components/event_listener/default.py:12` - `DefaultEventListener` class handles all message events and user interactions
- **Configuration**: `manifest.yaml` - Plugin metadata and configuration

### Core Functionality Flow
1. User sends "点歌" command with song name
2. `DefaultEventListener` searches music via external API (`http://lpz.chatc.vip/apiqq.php`)
3. Returns list of matching songs for user selection
4. User selects by number within 5 seconds
5. Plugin fetches song details and returns download/streaming links

### Key Components
- **Message Handling**: Uses LangBot's event system to process `PersonMessageReceived` and `GroupMessageReceived` events
- **State Management**: Maintains `user_searches` dictionary to track active song searches per user
- **API Integration**: Two main API calls - search music (returns list) and get song detail (returns download links)
- **Music Card Sender**: `utils/music_card.py:12` - Sends rich music cards via NapCat HTTP API using OneBot v11 protocol

## Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the plugin (through LangBot framework)
# This plugin runs as part of the LangBot ecosystem
```

### Dependencies
- `langbot-plugin`: Core plugin SDK
- `aiohttp`: Async HTTP client for all network requests and NapCat music card sending

### Recent Improvements
- **Async Network Requests**: Replaced synchronous `requests` with async `aiohttp` for better performance
- **URL Shortening**: Integrated multiple short URL services (TinyURL, is.gd, v.gd) to shorten download links
- **Enhanced User Experience**: Backup download links now use shortened URLs for better readability

## Important Implementation Details

### Event Handling Pattern
The plugin uses decorator-based event handlers (`@self.handler`) to listen for message events. All message processing happens in `components/event_listener/default.py:19-131`.

### User State Management
User search states are stored in memory (`self.user_searches`) with automatic cleanup after 5 seconds using asyncio tasks (`clear_user_search` method at `default.py:189`).

### API Response Structure
- Search API returns: `{'code': 200, 'data': [{'n': ..., 'song_title': ..., 'song_singer': ...}]}`
- Detail API returns: `{'code': 200, 'data': {'cover': ..., 'music_url': ..., 'link': ...}}`

### Message Chain Building
Uses LangBot's `MessageChain` with `Plain` and `Image` elements for rich message responses.

### NapCat Integration
- **Configuration**: Plugin accepts `napcat_url` config parameter (default: `http://127.0.0.1:3000`)
- **Music Cards**: Sends custom music cards using OneBot v11 protocol with title, audio URL, cover image
- **Fallback**: If NapCat is unavailable, falls back to traditional message format with download links
- **Environment Variables**: Supports `NAPCAT_ACCESS_TOKEN` for authentication if required