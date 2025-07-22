def execute(args): # the code calles this tool by calling the execute function, you can also use a async def

    def parse_args(arg_string):
        import shlex
        import ast
        args_dict = {}
        tokens = shlex.split(arg_string)
        for token in tokens:
            if '=' in token:
                key, value = token.split('=', 1)
                try:
                    value = ast.literal_eval(value)
                except Exception:
                    pass
                args_dict[key] = value
        return args_dict

    parsed = parse_args(args)
    first_arg = parsed.get('first_arg')
    second_arg = parsed.get('second_arg')

    return {
        'success': True,
        'result': f"Executed Example tool: first_arg = {first_arg}, second_arg = {second_arg}",
    }

if __name__ == "__main__":
    args = 'first_arg="Hello World" second_arg=False'
    print(execute(args))