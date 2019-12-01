from token import TokenType, tokenize

# from parse import parse


def parse_and_run(chunk: str):
    tokens = tokenize(chunk)
    for token in tokens:
        print(token)
    # ast = parse(tokens)
    # ast.execute()
