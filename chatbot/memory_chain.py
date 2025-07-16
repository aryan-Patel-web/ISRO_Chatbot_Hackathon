# chatbot/memory_chain.py

from langchain.memory import ConversationBufferMemory

def create_memory():
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
