"""
Tool loader system for Zen AI.
Handles loading and managing tools from the /tools directory.
"""

import os
import yaml
import importlib.util
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ToolLoader:
    """Loads and manages tools from the tools directory."""
    
    def __init__(self, tools_dir: str = "tools"):
        self.tools_dir = Path(tools_dir)
        self.tools = {}
        self.logger = logging.getLogger(__name__)
        self.load_tools()
    
    def load_tools(self):
        """Load all tools from the tools directory."""
        if not self.tools_dir.exists():
            self.logger.warning(f"Tools directory {self.tools_dir} does not exist")
            return
        
        for tool_folder in self.tools_dir.iterdir():
            if tool_folder.is_dir():
                self._load_tool(tool_folder)
    
    def _load_tool(self, tool_folder: Path):
        """Load a single tool from its folder."""
        config_file = tool_folder / "config.yaml"
        main_file = tool_folder / "main.py"
        
        if not config_file.exists():
            self.logger.warning(f"Tool {tool_folder.name} missing config.yaml")
            return
        
        if not main_file.exists():
            self.logger.warning(f"Tool {tool_folder.name} missing main.py")
            return
        
        try:
            # Load config
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load Python module
            # Replace dots in folder name with underscores for valid module name
            module_name = f"tool_{tool_folder.name.replace('.', '_')}"
            spec = importlib.util.spec_from_file_location(
                module_name, main_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Verify execute function exists
            if not hasattr(module, 'execute'):
                self.logger.error(f"Tool {tool_folder.name} missing execute function")
                return
            
            # Store tool - use folder name as tool name (e.g., main.speak)
            tool_name = tool_folder.name  # Use folder name instead of config name
            self.tools[tool_name] = {
                'config': config,
                'execute': module.execute,
                'folder': tool_folder
            }
            
            self.logger.info(f"Loaded tool: {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load tool {tool_folder.name}: {str(e)}")
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all loaded tools."""
        return self.tools.copy()
    
    def execute_tool(self, tool_name: str, args: str) -> Dict[str, Any]:
        """Execute a tool with the given arguments."""
        tool = self.get_tool(tool_name)
        
        if not tool:
            return {
                'success': False,
                'error': f"Tool '{tool_name}' not found"
            }
        
        import inspect
        import asyncio
        try:
            result = tool['execute'](args)
            if inspect.iscoroutine(result):
                # If already in an event loop, use create_task and run until complete
                try:
                    loop = asyncio.get_running_loop()
                    # For Flask, this should rarely happen, but just in case
                    fut = asyncio.ensure_future(result)
                    result = loop.run_until_complete(fut)
                except RuntimeError:
                    # No running loop, safe to use asyncio.run
                    result = asyncio.run(result)
            return result
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                'success': False,
                'error': f"Tool execution failed: {str(e)}"
            }
