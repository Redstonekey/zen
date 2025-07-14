# Zen - The AI

A unified AI presence system for developers that works across all devices with programmable tools and home automation focus.

## Overview

Zen is designed to be a smart home operating system for developers - where the AI is the interface, but the real power comes from the tools and automations that developers can build and integrate into their living/working space.

## Key Features

### Unified AI Presence
- Works across smartphones, laptops, smart speakers, and other smart home devices
- Shared knowledge base with persistent memory
- Cross-device continuity for seamless task management

### Developer-Focused Tool System
- Programmable tools with custom syntax
- Script execution capabilities (Python, shell scripts, etc.)
- Hardware control integration
- Unlimited automation possibilities

### Smart Home Integration
- Voice command processing
- Custom workflow automation
- Home automation focus over general chat
- Development assistance capabilities

## Quick Start

1. **Setup Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

2. **Run the Core System**
   ```bash
   python src/main.py
   ```

3. **Configure Your Devices**
   - See `config/` directory for device setup
   - Edit `config/devices.yaml` for your specific setup

## Project Structure

```
zen/
├── src/
│   ├── core/           # Core AI system
│   ├── devices/        # Device integrations
│   ├── tools/          # Developer tools
│   └── automation/     # Home automation scripts
├── config/             # Configuration files
├── scripts/            # Utility scripts
└── tests/             # Test files
```

## Development

- **Language**: Python 3.8+
- **Architecture**: Modular, extensible design
- **Focus**: Developer tools and home automation

## Contributing

This is a developer-focused project. Feel free to create custom tools and integrations for your specific needs.

## License

MIT License - See LICENSE file for details
