import flet as ft
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

# Initialize AI instance
ai = Gemini(
    api_key=config['ai']['api_key'],
    model="gemini-2.0-flash-lite",
    system_instruction=dynamic_instructions
)

# Initialize tool system
tool_system = ToolSystem()

def main(page: ft.Page):
    page.title = "Zen AI Chat"
    page.vertical_alignment = ft.MainAxisAlignment.START
    chat = ft.Column(scroll=ft.ScrollMode.ALWAYS)

    user_input = ft.TextField(hint_text="Type your message...", expand=True, disabled=False)
    send_btn = ft.ElevatedButton("Send")
    pause_btn = ft.ElevatedButton("Pause")
    continue_btn = ft.ElevatedButton("Continue")
    stop_btn = ft.ElevatedButton("Stop")
    controls_row = ft.Row([user_input, send_btn])

    def show_send():
        controls_row.controls.clear()
        controls_row.controls.append(user_input)
        controls_row.controls.append(send_btn)
        user_input.disabled = False
        page.update()

    def show_pause_stop():
        controls_row.controls.clear()
        controls_row.controls.append(pause_btn)
        controls_row.controls.append(stop_btn)
        user_input.disabled = True
        page.update()

    def show_continue_stop():
        controls_row.controls.clear()
        controls_row.controls.append(continue_btn)
        controls_row.controls.append(stop_btn)
        user_input.disabled = True
        page.update()


    running = {"value": False}
    paused = {"value": False}

    def pause_loop(e=None):
        paused["value"] = True
        show_continue_stop()

    def stop_loop(e=None):
        running["value"] = False
        paused["value"] = False
        show_send()

    def start_loop(msg):
        running["value"] = True
        paused["value"] = False
        show_pause_stop()
        while running["value"] and not paused["value"]:
            ai_response = ai.chat(msg, 'main')
            tool_commands = tool_system.process_response(ai_response)
            stop_found = False
            for cmd in tool_commands:
                if cmd.name == "main.speak":
                    result = tool_system.execute_command(cmd)
                    if result['success']:
                        chat.controls.append(ft.Text(f"AI: {result['result']}", color="#4CAF50"))
                    else:
                        chat.controls.append(ft.Text(f"❌ {result['error']}", color="#F44336"))
                    page.update()
                if cmd.name == 'main.stop':
                    running["value"] = False
                    logger.info("AI requested system shutdown")
                    break
            if stop_found:
                running["value"] = False
                paused["value"] = False
                show_send()
                break
            import time
            time.sleep(1)

    def on_user_input(e=None):
        msg = user_input.value.strip()
        if not msg:
            return
        chat.controls.append(ft.Text(f"You: {msg}", selectable=True))
        user_input.value = ""
        page.update()
        start_loop(msg)

    pause_btn.on_click = pause_loop
    stop_btn.on_click = stop_loop
    continue_btn.on_click = lambda e: [setattr(paused, "value", False), start_loop("")]
    user_input.on_submit = on_user_input
    send_btn.on_click = on_user_input

    # Add new chat icon (top right)
    def new_chat(e=None):
        chat.controls.clear()
        show_send()
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text("Zen AI Chat"),
        actions=[
            ft.IconButton(tooltip="New Chat", on_click=new_chat)
        ]
    )

    page.add(
        ft.Container(
            content=chat,
            expand=True,
            padding=10,
            bgcolor="#F5F5F5",  # Light grey
            border_radius=10,
            height=400
        ),
        controls_row
    )

    show_send()

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
