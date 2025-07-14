"""
Dynamic tool information system for Zen AI.
Automatically discovers available tools and generates instructions for the AI.
"""

import yaml
import logging
from typing import Dict, List
from pathlib import Path
from .tool_loader import ToolLoader


class ToolInfoGenerator:
    """Generates dynamic tool information for AI instructions."""
    
    def __init__(self, tools_dir: str = "tools"):
        self.tools_dir = Path(tools_dir)
        self.loader = ToolLoader(tools_dir)
        self.logger = logging.getLogger(__name__)
    
    def generate_tool_list(self) -> str:
        """Generate a formatted list of available tools for AI instructions."""
        tools = self.loader.list_tools()
        
        if not tools:
            return "No tools currently available."
        
        tool_list = []
        tool_list.append("Available Tools:")
        
        for tool_name, tool_info in tools.items():
            config = tool_info['config']
            description = config.get('description', 'No description available')
            
            # Add tool name and description
            tool_list.append(f"- **{tool_name}**: {description}")
            
            # Add usage examples if available
            examples = config.get('usage_examples', [])
            if examples:
                tool_list.append("  Examples:")
                for example in examples[:2]:  # Show max 2 examples
                    tool_list.append(f"    - {example}")
        
        return "\n".join(tool_list)
    
    def generate_tool_instructions(self) -> str:
        """Generate complete tool instructions for AI."""
        tool_list = self.generate_tool_list()
        
        instructions = f"""## Tool System
You can use tools by entering commands with this syntax: `{{tool {{name}} {{args}}}}`
- Tool names follow the format: `developer.project`
- Always use the exact tool names listed below

{tool_list}

## Tool Usage Rules:
- Use only the tools listed above
- Follow the exact syntax shown in examples
- Each tool call should be properly formatted
- You can only use one tool per response unless specifically instructed otherwise"""
        
        return instructions
    
    def update_ai_instructions(self, base_instructions: str) -> str:
        """Update AI instructions with current tool information."""
        # Generate current tool instructions
        tool_instructions = self.generate_tool_instructions()
        
        # Replace the tool system section in base instructions
        lines = base_instructions.split('\n')
        updated_lines = []
        skip_section = False
        
        for line in lines:
            if line.strip().startswith('## Tool System'):
                # Start of tool system section - replace with dynamic version
                updated_lines.extend(tool_instructions.split('\n'))
                skip_section = True
            elif line.strip().startswith('##') and skip_section:
                # End of tool system section - start including lines again
                skip_section = False
                updated_lines.append(line)
            elif not skip_section:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def get_tool_summary(self) -> Dict:
        """Get a summary of all available tools."""
        tools = self.loader.list_tools()
        summary = {
            'count': len(tools),
            'tools': {}
        }
        
        for tool_name, tool_info in tools.items():
            config = tool_info['config']
            summary['tools'][tool_name] = {
                'description': config.get('description', 'No description'),
                'developer': config.get('developer', 'Unknown'),
                'project': config.get('project', 'Unknown'),
                'parameters': config.get('parameters', [])
            }
        
        return summary
