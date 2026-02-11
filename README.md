# HiDOM - Hisense DOM Integration for Home Assistant

[![License](https://img.shields.io/github/license/undrianov-dot/hidom)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Component-blue)](https://www.home-assistant.io)

Integration for HiDOM (Hisense DOM) multi-split air conditioning systems with power meter support.

## Features

- 🌡️ Control all indoor units as separate climate entities
- 📊 Real-time energy consumption monitoring
- ⚡ Power meter integration
- 🔄 Automatic device discovery
- 🏠 Single hub for multiple devices

## Installation

### HACS (Recommended)
1. Open HACS in your Home Assistant instance
2. Go to Integrations
3. Click "+" and search for "HiDOM"
4. Install the integration
5. Restart Home Assistant

### Manual Installation
1. Copy the `hidom` folder to `custom_components/` in your Home Assistant configuration
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "HiDOM" and follow the setup instructions

## Configuration

1. In Home Assistant, go to Settings → Devices & Services → Integrations
2. Click "+ Add Integration"
3. Search for "HiDOM"
4. Enter the IP address of your HiDOM device (e.g., `10.99.3.100`)
5. Click "Submit"

## Supported Devices

- Hisense Multi-IDU systems with DOM controller
- Hi-Dom III and similar models
- Systems with built-in power meter

## Services

Available services:
- `hidom.refresh_devices`: Force refresh all devices
- `hidom.set_global_temperature`: Set temperature for all devices

## Development

### Requirements
- Python 3.9+
- Home Assistant 2023.1+
- aiohttp 3.8.0+

### Testing
```bash
pytest tests/