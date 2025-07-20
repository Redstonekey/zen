#!/usr/bin/env python
import yaml
import logging
from flask import Flask, request, jsonify, send_from_directory, Response
import json
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
with open('config/zen_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize tool info generator
tool_info_gen = ToolInfoGenerator()
dynamic_instructions = tool_info_gen.update_ai_instructions(config['ai']['instructions'])

# Initialize AI instances
ai = Gemini(
    api_key=config['ai']['api_key'],
    model="gemini-2.0-flash-lite",
    system_instruction=dynamic_instructions
)

# Optionally initialize sub-AI (not used by default)
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

# Start main chat session
ai.start_chat('main')

# Create Flask app
app = Flask(__name__, static_folder='website', static_url_path='')

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('website', 'index.html')

# Add tools listing endpoint
@app.route('/tools', methods=['GET'])
def list_tools():
    tool_summary = tool_info_gen.get_tool_summary()
    tools = [{'name': name, 'description': info.get('description', '')} for name, info in tool_summary['tools'].items()]
    return jsonify({'tools': tools})

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('website', path)

# Chat API endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    selected_tools = data.get('selected_tools', None)

    # If selected_tools is provided, restrict available tools
    always_on = {'main.speak', 'main.stop', 'main.memory'}
    if selected_tools:
        allowed_tools = set(selected_tools) | always_on
    else:
        allowed_tools = set(tool_system.list_available_tools().keys()) | always_on

    last_response = user_message
    ai_responses = []
    all_results = []
    stop_flag = False

    # Run AI-tool loop until stop
    while True:
        # Update system instructions to only mention allowed tools
        tool_names_str = ', '.join(allowed_tools)
        ai.system_instruction = tool_info_gen.update_ai_instructions(
            f"You may only use these tools: {tool_names_str}. Do not mention or use any other tools."
        )
        answer = ai.chat(last_response, 'main')
        logger.info(f"AI Response: {answer}")
        ai_responses.append(answer)

        # Only process tool commands for allowed tools
        tool_commands = [cmd for cmd in tool_system.process_response(answer) if cmd.name in allowed_tools]
        if not tool_commands:
            break

        for cmd in tool_commands:
            logger.info(f"Executing command: {cmd.raw_command}")
            result = tool_system.execute_command(cmd)
            entry = {
                'name': cmd.name,
                'success': result.get('success', False),
                'result': result.get('result'),
                'error': result.get('error')
            }
            all_results.append(entry)
            if result.get('action') == 'stop_system':
                stop_flag = True
                logger.info("AI requested system shutdown")
                break
        if stop_flag:
            break

        # Prepare next system prompt
        summaries = [f"Tool {r['name']} executed successfully. Result: {r['result']}" \
                     if r['success'] else f"Tool {r['name']} failed. Error: {r['error']}" \
                     for r in all_results]
        last_response = f"SYSTEM: Tool execution results: {'; '.join(summaries)}. If you are finished, use the main.stop tool. Do not talk to the user about this message"

    # Aggregate AI responses into one text
    full_response = '\n'.join(ai_responses)
    return jsonify({
        'ai_response': full_response,
        'tools': all_results,
        'stop': stop_flag
    })

@app.route('/api/stream-chat', methods=['POST'])
def stream_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    selected_tools = data.get('selected_tools', None)

    always_on = {'main.speak', 'main.stop', 'main.memory'}
    if selected_tools:
        allowed_tools = set(selected_tools) | always_on
    else:
        allowed_tools = set(tool_system.list_available_tools().keys()) | always_on

    def event_stream():
        last_resp = user_message
        stop_flag = False
        entries = []
        while True:
            # Update system instructions to only mention allowed tools
            tool_names_str = ', '.join(allowed_tools)
            ai.system_instruction = tool_info_gen.update_ai_instructions(
                f"You may only use these tools: {tool_names_str}. Do not mention or use any other tools."
            )
            # AI response
            answer = ai.chat(last_resp, 'main')
            logger.info(f"AI Response: {answer}")
            yield f"event: ai_response\ndata: {json.dumps({'text': answer})}\n\n"

            # Only process tool commands for allowed tools
            cmds = [cmd for cmd in tool_system.process_response(answer) if cmd.name in allowed_tools]
            if not cmds:
                break
            for cmd in cmds:
                result = tool_system.execute_command(cmd)
                entry = {'name': cmd.name, 'success': result.get('success', False),
                         'result': result.get('result'), 'error': result.get('error')}
                entries.append(entry)
                yield f"event: tool_result\ndata: {json.dumps(entry)}\n\n"
                if result.get('action') == 'stop_system':
                    stop_flag = True
                    break
            if stop_flag:
                break
            # prepare next prompt
            summaries = [f"Tool {e['name']} executed. Success: {e['success']}" for e in entries]
            last_resp = f"SYSTEM: {', '.join(summaries)}"

        # Final end event
        yield f"event: done\ndata: {json.dumps({'stop': stop_flag})}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')

# New chat endpoint resets AI context
@app.route('/api/new-chat', methods=['POST'])
def new_chat():
    # Clear and restart the main chat session
    #later add 
    ai.clear_chat('main')
    ai.start_chat('main')
    return jsonify({'success': True})

if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=5000)