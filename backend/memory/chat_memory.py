chat_history=[]

def add_message(role: str, content: str):
    chat_history.append({
        "role": role,
        "content": content
    })

    #prevent unlimited growth
    if len(chat_history)>20:
        chat_history.pop(0)

def get_history():
    return chat_history

def clear_history():
    chat_history.clear()