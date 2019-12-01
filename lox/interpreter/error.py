def report(line: int, where: str, message: str):
    print(f"Error at line {line}{(', ' + where) if where != '' else ''}: {message}")
    return True


def error(line: int, message: str):
    return report(line, "", message)
