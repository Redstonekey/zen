# Zen AI - Unified AI Presence System

A unified AI presence system for developers that works seamlessly across all devices (smartphone, laptop, Alexa, smart home devices) with programmable tools and home automation focus.

## 🌟 Vision & Goals

Zen AI aims to create a single, intelligent AI assistant that:
- Maintains **continuity across all your devices** - start a task on your phone, continue on your laptop
- Provides **extensible tool system** - easily add custom tools and integrations
- Supports **sub-AI orchestration** - spawn specialized AIs for complex tasks
- Offers **comprehensive memory system** - remembers context and learns from interactions
- Enables **home automation** - control and monitor smart home devices
- Features **marketplace integration** - discover and install community tools

## 🚀 Current Features (Built)

### ✅ Core AI System
- **Multi-Chat Support**: The `Gemini` class supports multiple simultaneous chat sessions
- **Dynamic Tool Discovery**: Automatically discovers and loads tools from `/tools/` directory
- **Tool Command Parsing**: Parses tool commands from AI responses in format `{tool {name} {args}}`
- **Configuration Management**: YAML-based configuration system

### ✅ Tool System Architecture
- **Dynamic Tool Loading**: Tools are automatically discovered from folder structure
- **Tool Folder Convention**: Each tool stored in `developer.project` format (e.g., `main.speak`)
- **Tool Configuration**: Each tool has `config.yaml` with metadata and usage examples
- **Tool Execution**: Each tool has `main.py` with `execute(args)` function
- **Auto-updating Instructions**: AI instructions dynamically updated with available tools

### ✅ Built-in Tools
- **`main.speak`**: Print text to console for AI communication
- **`main.stop`**: Stop the main AI loop gracefully

### ✅ Infrastructure
- **Logging System**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Robust error handling for tool execution and AI communication
- **Type Hints**: Full Python type hint support for better development experience

## 🎯 Planned Features (Roadmap)

### 🔄 Sub-AI Management
- **Sub-AI Spawning**: Main AI can create specialized sub-AIs for specific tasks
- **Task Delegation**: Distribute complex tasks across multiple sub-AIs
- **Sub-AI Coordination**: Manage communication between sub-AIs and main AI
- **Task Reporting**: Sub-AIs report completion status back to main AI

### 🧠 Memory System
- **Short-term Memory**: 24-hour memory for current tasks and temporary notes
- **Long-term Memory**: Permanent storage for important information and preferences
- **Calendar Memory**: Summarized daily activities and historical context
- **Memory Tools**: `memory.read` and `memory.write` tools for memory management

### 🔧 Standard Tools Suite
- **Memory Tool**: Read and write memory entries across all memory types
- **File Tool**: Read and write files on the local system
- **Web Tool**: Search the web and retrieve information
- **Notification Tool**: Send notifications to user across devices

### 🏠 Device Integration
- **Cross-Device Continuity**: Seamless task continuation across devices
- **Smart Home Integration**: Control lights, thermostats, and other IoT devices
- **Mobile App**: Smartphone integration for on-the-go access
- **Voice Assistant**: Alexa and Google Assistant integration

### 🛒 Marketplace System
- **Tool Marketplace**: Discover and install community-created tools
- **Tool Search**: AIs can search for and install tools they need
- **Tool Ratings**: Community ratings and reviews for tools
- **Tool Publishing**: Easy publishing system for developers

### 💾 Supabase Integration
- **Database Backend**: Full Supabase integration for data persistence
- **User Management**: Authentication and user account system
- **Real-time Sync**: Real-time synchronization across devices
- **Cloud Storage**: Cloud-based memory and configuration storage

## 🏗️ Architecture

```
Zen AI System
├── Main AI (Orchestrator)
│   ├── Chat Management
│   ├── Tool Execution
│   └── Sub-AI Coordination
├── Sub-AIs (Specialized)
│   ├── Task Planner
│   ├── Researcher
│   └── Monitor
├── Tool System
│   ├── Dynamic Loading
│   ├── Command Parsing
│   └── Execution Engine
├── Memory System
│   ├── Short-term (24h)
│   ├── Long-term (Permanent)
│   └── Calendar (Summarized)
└── Device Integration
    ├── Cross-Platform API
    ├── Real-time Sync
    └── Hardware Control
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/zen-ai.git
   cd zen-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API key in `config/zen_config.yaml`:
   ```yaml
   ai:
     api_key: "your-gemini-api-key-here"
   ```

4. Run the system:
   ```bash
   python main.py
   ```

## 🔧 Development

### Creating Custom Tools
1. Create a new folder in `/tools/` with format `developer.project`
2. Add `config.yaml` with tool metadata:
   ```yaml
   name: "developer.project"
   description: "Tool description"
   developer: "developer"
   project: "project"
   parameters:
     - name: "param1"
       type: "string"
       required: true
       description: "Parameter description"
   usage_examples:
     - '{tool developer.project param1="value"}'
   ```

3. Add `main.py` with execute function:
   ```python
   def execute(args):
       """Execute the tool with given arguments"""
       try:
           # Tool logic here
           return {
               'success': True,
               'result': 'Tool executed successfully'
           }
       except Exception as e:
           return {
               'success': False,
               'error': str(e)
           }
   ```

### Tool Command Syntax
Tools are executed using the syntax: `{tool {name} {args}}`

Examples:
- `{tool main.speak text="Hello World"}`
- `{tool memory.write entry="Important note" type="long"}`
- `{tool home.light room="living_room" action="on"}`



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 📈 Project Status

**Current Version**: 0.1.0 (Alpha)
- ✅ Core AI system with multi-chat support
- ✅ Dynamic tool loading and execution
- ✅ Basic tool command parsing
- ✅ Configuration management
- 🔄 Sub-AI management (In Progress)
- 🔄 Memory system (Planned)
- 🔄 Standard tools suite (Planned)
- 🔄 Device integration (Planned)
- 🔄 Marketplace system (Planned)

---

*Zen AI - Bringing unified intelligence to your digital life* 🧘‍♂️🤖
