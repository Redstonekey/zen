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
debug = False
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
user_task = "hey could you create a new file called receptideas.txt in the classic windows documents folder and write a recipe idea in it a cocktail recipe pls?"
last_response = user_task  # Start with the initial user task

ai.start_chat('main')

while running:
    # Send the last response (or initial task) to the AI
    answer = ai.chat(last_response, 'main')
    print(f"AI Response: {answer}")
    # Process the AI's response for tool commands
    tool_commands = tool_system.process_response(answer)

    if not tool_commands:
        # If there are no tool commands, treat it as a spoken response
        # and prepare to continue the loop, asking the AI what's next.
        last_response = "What is the next step? If you are finished, use the main.stop tool."
        continue

    # Execute tool commands
    execution_results = []
    for cmd in tool_commands:
        print(f"Executing command: {cmd.raw_command}")
        result = tool_system.execute_command(cmd)
        
        if result['success']:
            print(f"✅ Tool executed successfully: {result['result']}")
            execution_results.append(f"Tool {cmd.name} executed successfully. Result: {result['result']}")
            if result.get('action') == 'stop_system':
                running = False
                logger.info("AI requested system shutdown")
                break 

        else:
            print(f"❌ Tool execution failed: {result['error']}")
            execution_results.append(f"Tool {cmd.name} failed. Error: {result['error']}")
    
    if not running:
        break

    # Feed the combined results of tool executions back to the AI for the next turn
    last_response = f"SYSTEM: Tool execution results: {'; '.join(execution_results)}. Your task is still: '{user_task}'. What is the next step? If you are finished, use the main.stop tool."

ai.clear_all_chats()