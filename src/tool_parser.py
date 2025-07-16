"""
Tool command parser for Zen AI system.
Handles parsing of tool commands in the format: {tool {name} {args}}
"""

import re
import logging
from typing import List
from dataclasses import dataclass
from .tool_loader import ToolLoader


@dataclass
class ToolCommand:
    """Represents a parsed tool command."""
    name: str
    args: str
    raw_command: str


class ToolParser:
    """Parses and extracts tool commands from AI responses."""
    
    def __init__(self):
        # Regex to match {tool name [args]} across multiple lines, with optional args
        # Use DOTALL so args can include newlines
        self.tool_pattern = re.compile(
            r'\{tool\s+([^\s\}]+)(?:\s+([\s\S]+?))?\}',
            re.DOTALL
        )
        self.logger = logging.getLogger(__name__)
    
    def parse_commands(self, text: str) -> List[ToolCommand]:
        """
        Parse tool commands from text.
        
        Args:
            text: The text to parse for tool commands
            
        Returns:
            List of ToolCommand objects found in the text
        """
        commands = []
        matches = self.tool_pattern.findall(text)
        
        for match in matches:
            tool_name = match[0]
            raw_args = match[1] or ''
            tool_args = raw_args.strip()
            # Build raw_command with or without args
            if tool_args:
                raw_command = f"{{tool {tool_name} {tool_args}}}"
            else:
                raw_command = f"{{tool {tool_name}}}"
            
            commands.append(ToolCommand(
                name=tool_name,
                args=tool_args,
                raw_command=raw_command
            ))
            
        return commands
    
    def has_tool_commands(self, text: str) -> bool:
        """
        Check if text contains any tool commands.
        
        Args:
            text: The text to check
            
        Returns:
            True if tool commands are found, False otherwise
        """
        return bool(self.tool_pattern.search(text))
    
    def extract_non_tool_text(self, text: str) -> str:
        """
        Extract text that is not part of tool commands.
        
        Args:
            text: The original text
            
        Returns:
            Text with tool commands removed
        """
        return self.tool_pattern.sub('', text).strip()


class ToolSystem:
    """Main tool system for parsing and executing tool commands."""
    
    def __init__(self):
        self.parser = ToolParser()
        self.loader = ToolLoader()
        self.logger = logging.getLogger(__name__)
    
    def process_response(self, response: str) -> List[ToolCommand]:
        """
        Process an AI response and return tool commands found.
        
        Args:
            response: The AI response text
            
        Returns:
            List of ToolCommand objects found in the response
        """
        if not self.parser.has_tool_commands(response):
            return []
        
        commands = self.parser.parse_commands(response)
        self.logger.info(f"Found {len(commands)} tool commands in response")
        
        return commands
    
    def execute_command(self, command: ToolCommand) -> dict:
        """
        Execute a tool command.
        
        Args:
            command: The ToolCommand to execute
            
        Returns:
            Dictionary with execution result
        """
        return self.loader.execute_tool(command.name, command.args)
    
    def list_available_tools(self) -> dict:
        """List all available tools."""
        return self.loader.list_tools()
