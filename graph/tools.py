from weaviate.classes.query import Filter, MetadataQuery
from langchain_core.tools import tool
from typing import Optional, List
from langchain_openai import OpenAIEmbeddings
import json
import os
import weaviate
import psycopg2
import re
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from prompts import *
from connections.connect import get_weaviate_client, _pg_ro_conn, _rows_to_table

load_dotenv()

weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")


client = get_weaviate_client()

@tool(description=weaviate_tool_describtion)
def weaviate_func(id_doc:Optional[str], query: str, organization: str , section: Optional[int], type_doc: Optional[str]) -> str:
    # print(f"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
    chunks = client.collections.use("Chunk")
    event = {
    "__event__": "weaviate_query",
    "query": query,
    "filters": {
        "id_doc": id_doc,
        "organization": organization,
        "section": section,
        "type_doc": type_doc
        }
    }

    emb = OpenAIEmbeddings(model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY"))
    vec = emb.embed_query(query)
    # print(f"ssssssssssssss   {query} {organization} {section} {type_doc}")
    filters: List[Filter] = []
    if id_doc is not None: filters.append(Filter.by_property("id_doc").equal(id_doc))
    if organization: filters.append(Filter.by_property("organization").like(f"*{organization}*"))  
    if section is not None: filters.append(Filter.by_property("section").equal(section))
    if type_doc: filters.append(Filter.by_property("type_doc").equal(type_doc))
    where_filter = None
    if filters:
        where_filter = Filter.all_of(filters)
    res = chunks.query.hybrid(
        query=query,
        alpha=0.6,
        limit=10,
        vector=vec,
        filters=where_filter, 
        return_metadata=MetadataQuery(score=True),
    )
    if not res.objects:
        return "Ничего не найдено."
    lines = []
    for i, obj in enumerate(res.objects):
        # print(f"Obj {i}: {obj}")
        p = obj.properties or {}
        txt = (p.get("content") or "").replace("\n", " ").strip()[:400]
        src = p.get("source") or ""
        page = p.get("page")
        meta = f"{src} p.{page}" if src or page else ""
        lines.append(f"[{i+1}] {meta} — {txt}")
        print(f"                     {txt}")
    # client.close()    
    return json.dumps({ "event": event, "result": "\n".join(lines) }, ensure_ascii=False)


@tool(description=sql_tool_describtion)
def db_sql(sql: str, max_rows: int = 1000) -> str:
    print("db_sql called with:", sql)
    event = {"__event__": "sql_query", "query": sql}
    q = sql.strip().rstrip(";")
    q_low = re.sub(r"\s+", " ", q.lower()).strip()

    if not (q_low.startswith("select") or q_low.startswith("with") or q_low.startswith("explain ")):
        return "Запрещено: допускаются только SELECT/WITH/EXPLAIN (без ANALYZE)."
    if "explain analyze" in q_low:
        return "Запрещено: EXPLAIN ANALYZE."
    q = q.split(";")[0]
    if (q_low.startswith("select") or q_low.startswith("with")) and not re.search(r"\blimit\b", q_low):
        q = f"{q} LIMIT {max_rows}"
    try:
        conn = _pg_ro_conn()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q)
            try:
                rows = cur.fetchall()
            except psycopg2.ProgrammingError:
                rows = []
        conn.close()
        result = _rows_to_table(rows, max_rows)
        print("db_sql result:", result)
        return json.dumps({ "event": event, "result": result }, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка {e}")
        return f"SQL error: {e}"
    finally:
        conn.close()