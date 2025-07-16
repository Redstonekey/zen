import yaml
import logging
from flask import Flask, request, jsonify
from src.ai.gemini import Gemini
from src.tool_parser import ToolSystem
from src.tool_info import ToolInfoGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
with open('config/zen_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize AI and tools
tool_info_gen = ToolInfoGenerator()
base_instructions = config['ai']['instructions']
dynamic_instructions = tool_info_gen.update_ai_instructions(base_instructions)
ai = Gemini(
    api_key=config['ai']['api_key'],
    model="gemini-2.0-flash-lite",
    system_instruction=dynamic_instructions
)
# start main chat session
ai.start_chat('main')

tool_system = ToolSystem()

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'Empty message'}), 400

    # AI response
    ai_response = ai.chat(message, 'main')
    # Process tool commands
    commands = tool_system.process_response(ai_response)
    results = []
    for cmd in commands:
        res = tool_system.execute_command(cmd)
        results.append({
            'name': cmd.name,
            'success': res.get('success', False),
            'result': res.get('result'),
            'error': res.get('error')
        })

    return jsonify({
        'ai_response': ai_response,
        'tools': results
    })

if __name__ == '__main__':
    app.run(port=5000)
