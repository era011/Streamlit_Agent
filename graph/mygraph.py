from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from graph.tools import *
from prompts import *
import json
import os
from graph.responce_formats import evaluator_response, planner_response

load_dotenv()

stream_llm = ChatOpenAI(
    model="gpt-5.2",
    streaming=True,
    api_key=os.getenv("OPENAI_API_KEY"),
)

llm = ChatOpenAI(
    model="gpt-5.2",
    temperature=0,
    streaming=False,   # КЛЮЧЕВО
    api_key=os.getenv("OPENAI_API_KEY"),
    disable_streaming=True
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    organization: str | None
    plan: list[str] | None
    route: str | None  # rag | sql | none
    tool_ok: bool | None
    tool_calls:int






def planner_node(state: State) -> dict:
    system = {
        "role": "system",
        "content": planner_prompt
    }
    tool_calls={
        "role": "tool_calls_number",
        "content": state.get('tool_calls')
    }
    msgs = state["messages"]
    ai = llm.with_structured_output(planner_response).invoke([system] + msgs)
    return {
        "plan": ai.plan,
        "route": ai.route,
        "__event__": "planner",
    }
   

rag_llm = llm.bind_tools([weaviate_func])

def rag_node(state: State) -> dict:
    system = {
        "role": "system",
        "content": rag_prompt(state['organization'])
    }
    msgs = state["messages"]
    ai = rag_llm.invoke([system] + msgs)
    return {"messages": [ai],
            "tool_calls": state.get("tool_calls", 0) + 1}

sql_llm = llm.bind_tools([db_sql])

def sql_node(state: State) -> dict:
    system = {
        "role": "system",
        "content": sql_prompt(state['organization'])
    }
    msgs = state["messages"]
    ai = sql_llm.invoke([system] + msgs)
    return {"messages": [ai],
            "tool_calls": state.get("tool_calls", 0) + 1}


def evaluator_node(state: State) -> dict:
    system = {
        "role": "system",
        "content": evaluator_prompt
    }
    msgs = state["messages"]
    ai = llm.with_structured_output(evaluator_response).invoke([system] + msgs)
    ok = ai.evaluation
    return {"tool_ok": ok}


def final_node(state: State) -> dict:
    system = {
        "role": "system",
        "content": final_prompt
    }
    msgs = state["messages"]
    ai = stream_llm.invoke([system] + msgs)
    return {"messages": [ai]}






def route_selector(state: State) -> str:
    return state["route"] or "none"


rag_tools = ToolNode([weaviate_func])
sql_tools = ToolNode([db_sql])

builder = StateGraph(State)

builder.add_node("planner", planner_node)

# RAG
builder.add_node("rag", rag_node)
builder.add_node("rag_tools", rag_tools)
builder.add_edge("rag", "rag_tools")
builder.add_edge("rag_tools", "evaluator")

# SQL
builder.add_node("sql", sql_node)
builder.add_node("sql_tools", sql_tools)
builder.add_edge("sql", "sql_tools")
builder.add_edge("sql_tools", "evaluator")

builder.add_node("evaluator", evaluator_node)
builder.add_node("final", final_node)

builder.set_entry_point("planner")

builder.add_conditional_edges(
    "planner",
    route_selector,
    {
        "rag": "rag",
        "sql": "sql",
        "none": "final"
    }
)

builder.add_conditional_edges(
    "evaluator",
    lambda s: "final" if s.get("tool_ok") or s.get("tool_calls", 0) >= 10 else "planner",
    {
        "final": "final",
        "planner": "planner"
    }
)

builder.add_edge("final", END)

graph = builder.compile()


# state={
#     'messages':[{'role':'user', 'content':'лучший сотрудник'},
#                 # {'role':'ai','content':'не понятно'},
#                 # {'role':'user','content':'хочу узнать о конкурсе лучший сотрудник'},
#                 ],
#     'organization': None,
#     'plan': None,
#     'route': None,  # rag | sql | none

#     # контроль
#     'tool_ok': None
# }

# import asyncio

# async def run():
#     async for i in graph.astream_events(state):
#         print("=========================================================================")
#         # print(i)
#         print(i['event'])
#         # print(i['data'].keys())
#         print(i['data'])
    

# asyncio.run(run())
