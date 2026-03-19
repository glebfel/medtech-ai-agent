from langgraph.checkpoint.postgres import PostgresSaver


def create_checkpointer(database_url: str) -> PostgresSaver:
    """Create a PostgreSQL-backed checkpointer for persistent conversation memory.

    Returns a context manager — use with `with` statement.
    The checkpointer stores full conversation state per thread_id,
    enabling memory across restarts.
    """
    return PostgresSaver.from_conn_string(database_url)
