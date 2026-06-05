from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from typing import Annotated, TypedDict

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

import requests
import random
import asyncio

load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')


@tool
def Calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """

    try:
        if operation == "add":
            result = first_num + second_num

        elif operation == "sub":
            result = first_num - second_num

        elif operation == "mul":
            result = first_num * second_num

        elif operation == "div":
            if(second_num == 0):
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num

        else:
            return {"error": "Invalid operation"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}
    
# Make tools list
tools = [Calculator]

# Make the LLM tool-aware
llm_with_tool = llm.bind_tools(tools=tools)

# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def build_graph():
    async def chat_node(state: ChatState):
        """LLM node that may answer or request a tool call."""
        messages = state['messages']
        response = await llm_with_tool.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools=tools)

    # Graph structure
    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()
    return chatbot



async def main():

    chatbot = build_graph()

    # running the graph
    result = await chatbot.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content="Find the modulus of 132354 and 23  and give answer like a cricket commentator.  "
                )
            ]
        }
    )

    print(result['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())