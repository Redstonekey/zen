def execute(args):
    print('Test tool execution')
    print(args)
    return {
        'success': True,
        'result': f"Executed Test tool",
        'action': 'TEST'
    }