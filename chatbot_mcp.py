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
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')



# MCP client for local FastMCP server
client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio",
            "command": "python",
            "args": [r"C:\Programming\LangGraph_ChatBot\main.py"],
        }
    }
)

    
# # Make tools list
# tools = [Calculator]

# # Make the LLM tool-aware
# llm_with_tool = llm.bind_tools(tools=tools)

# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def build_graph():

    tools = await client.get_tools()

    llm_with_tool = llm.bind_tools(tools=tools)

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

    chatbot = await build_graph()

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