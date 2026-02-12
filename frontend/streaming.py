import asyncio
import json


def sync_stream(async_gen):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    agen = async_gen.__aiter__()

    try:
        while True:
            try:
                item = loop.run_until_complete(agen.__anext__())
                yield item
            except StopAsyncIteration:
                break
    finally:
        loop.close()

async def stream_text(graph, messages, organization):
    state = {"messages": messages, "organization": organization, "tool_calls": 0}
    async for ev in graph.astream_events(state, version="v2"):
        #print("EVENT:", ev["event"], "DATA:", str(ev.get("data"))[:300])
        if ev["event"] == "on_chat_model_stream":
            delta = ev["data"]["chunk"].content or ""
            if delta:
                yield {"type": "text", "data": delta}

        if ev["event"] == "on_tool_end":
            output = ev["data"].get("output")
            print("RAW OUTPUT:", type(output), str(output)[:300])
        
            if hasattr(output, "content"):
                output = output.content
        
            if isinstance(output, str):
                try:
                    output = json.loads(output)
                except Exception:
                    yield {"type": "text", "data": output}
                    continue
        
            if isinstance(output, dict):
                evt = output.get("event", {})
                if evt.get("__event__") == "weaviate_query":
                    filters = evt.get("filters", {})
                    filters_str = ", ".join(
                        f"{k}={v}" for k, v in filters.items() if v not in (None, "")
                    )
                    query_info = evt.get("query", "")
                    if filters_str:
                        query_info += f"  ({filters_str})"
                    yield {"type": "weaviate", "data": query_info}
                    yield {"type": "weaviate_result", "data": output.get("result", "")}
                elif evt.get("__event__") == "sql_query":
                    yield {"type": "sql", "data": evt.get("query", "")}
                    yield {"type": "sql_result", "data": output.get("result", "")}

        if (
            ev["event"] == "on_chain_end"
            and isinstance(ev.get("data"), dict)
            and isinstance(ev["data"].get("output"), dict)
            and "plan" in ev["data"]["output"]
        ):
            yield {
                "type": "plan",
                "data": ev["data"]["output"]["plan"]
            }