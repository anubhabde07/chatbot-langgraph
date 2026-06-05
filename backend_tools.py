from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

import requests
import random

load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')

# Tools
search_tools = DuckDuckGoSearchRun()

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
    

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL.
    """

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}=AAPL&apikey=PLDKFPOVH33YDFOJ"

    res = requests.get(url=url)

    return res.json()

# Make tools list
tools = [search_tools, Calculator, get_stock_price]

# Make the LLM tool-aware
llm_with_tool = llm.bind_tools(tools=tools)


# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]    # Annotated[type, metadata]


def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state['messages']
    response = llm_with_tool.invoke(messages)
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
