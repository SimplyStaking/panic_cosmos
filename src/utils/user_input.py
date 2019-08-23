def prompt(prompt_msg: str) -> str:
    # This function was added just for improved testability
    return input(prompt_msg)


def yn_prompt(prompt_msg: str) -> bool:
    while True:
        input_str = prompt(prompt_msg)
        if input_str.lower() in ['y', '']:
            return True
        elif input_str.lower() == 'n':
            return False
        else:
            print('Invalid input.')
