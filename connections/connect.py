import os 
from dotenv import load_dotenv
import weaviate
import psycopg2

load_dotenv()

def get_weaviate_client():
    url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    host = url.replace("http://","").replace("https://","").split(":")[0]
    port = int(url.split(":")[-1]) if ":" in url else 8080
    return weaviate.connect_to_local(
        host=host,
        port=port,
        grpc_port=50051,
        headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
    )

_wv_client = None

def set_weaviate_client(client) -> None:
    global _wv_client
    _wv_client = client

def _pg_ro_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "knowledgebase"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        options="-c statement_timeout=2000 -c default_transaction_read_only=on -c search_path=public"
    )


def _rows_to_table(rows: list[dict], max_rows: int) -> str:
    if not rows:
        return "0 rows."
    cols = list(rows[0].keys())
    lines = [" | ".join(cols)]
    for r in rows[:max_rows]:
        lines.append(" | ".join([str(r.get(c, "")) for c in cols]))
    more = "" if len(rows) <= max_rows else f"\n… truncated to {max_rows} rows."
    return "\n".join(lines) + more    