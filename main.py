import yaml
import logging
from src.ai.gemini import Gemini
from src.tool_parser import ToolSystem
from src.tool_info import ToolInfoGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration from YAML file
with open('config/zen_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize tool info generator
tool_info_gen = ToolInfoGenerator()

# Generate dynamic instructions with current tool information
base_instructions = config['ai']['instructions']
dynamic_instructions = tool_info_gen.update_ai_instructions(base_instructions)

# Initialize AI instances with dynamic instructions
ai = Gemini(
    api_key=config['ai']['api_key'],
    model="gemini-2.0-flash-lite",
    system_instruction=dynamic_instructions
)
sub_ai = Gemini(
    api_key=config['ai']['api_key'],
    model="gemini-2.0-flash-lite",
    system_instruction=config['ai']['sub_ai_instructions']
)

# Initialize tool system
tool_system = ToolSystem()

# Show available tools at startup
tool_summary = tool_info_gen.get_tool_summary()
logger.info(f"Loaded {tool_summary['count']} tools: {', '.join(tool_summary['tools'].keys())}")

running = True

ai.start_chat('main')
print('chat starts:')
while running:
    answer = ai.chat("hey ehm could you use the speak tool only twice not infinite long and count the times and tell them the tool!", 'main')
    print(f"AI Response: {answer}")
    tool_commands = tool_system.process_response(answer)
    
    for cmd in tool_commands:
        print(f"Executing command: {cmd.raw_command}")
        result = tool_system.execute_command(cmd)
        
        if result['success']:
            print(f"✅ Tool executed successfully: {result['result']}")
            
            # Check if the stop tool was executed
            if result.get('action') == 'stop_system':
                running = False
                logger.info("AI requested system shutdown")
                break
        else:
            print(f"❌ Tool execution failed: {result['error']}")


ai.clear_all_chats()