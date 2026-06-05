from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3

load_dotenv()


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]    # Annotated[type, metadata]


def chat_node(state: ChatState):
    llm = ChatOpenAI(model='gpt-4o-mini')

    messages = state['messages']

    response = llm.invoke(messages)

    return {'messages': [response]}


conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

# add node
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# compile
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)