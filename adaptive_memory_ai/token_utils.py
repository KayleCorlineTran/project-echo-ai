import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text):
    return len(encoding.encode(text))


def count_message_tokens(messages):
    total = 0

    for message in messages:
        total += count_tokens(message["content"])

    return total