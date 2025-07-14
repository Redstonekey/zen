def execute(args: str) -> dict:
    """
    Speak tool execution function - prints text to console.
    
    Args:
        args: The arguments string from the tool command
    
    Returns:
        dict: Result with success/error information
    """
    try:
        # Simple argument parsing for text parameter
        if 'text=' in args:
            text = args.split('text=')[1].strip('"\'')
            print(f"🔊 Zen AI: {text}")
            return {
                'success': True,
                'result': f"Spoken: {text}"
            }
        else:
            return {
                'success': False,
                'error': "Missing required parameter: text"
            }
    except Exception as e:
        return {
            'success': False,
            'error': f"Tool execution failed: {str(e)}"
        }
