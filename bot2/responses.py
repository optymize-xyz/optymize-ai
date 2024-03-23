from random import choice, randint


def get_response(user_input: str, rag_chain) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Ask me anything u want'
    elif 'hello' in lowered:
        return "Hiiiiiiii"
    else:
        return rag_chain.invoke(lowered)