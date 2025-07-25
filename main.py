# main.py

from core_mcp.mcp import MCPMessage
from agents.ingestion_agent import run_ingestion_agent
from agents.indexagent import handle_index_message
from agents.retrieval_agent import handle_retrieval_message
from agents.llmresponse_agent import handle_llm_message

def run_pipeline(file_paths, user_query):
    final_answer = ""
    context_used = []

    for file_path in file_paths:
        doc_type = file_path.split(".")[-1]
        
        # Step 1: Ingestion
        msg1 = MCPMessage(
            sender="Main",
            receiver="IngestionAgent",
            msg_type="ingest",
            payload={"file_path": file_path, "doc_type": doc_type}
        )
        msg2 = run_ingestion_agent(file_path)

        # Step 2: Indexing
        msg3 = handle_index_message(msg2)

    # Step 3: Retrieval (after all files indexed)
    msg4 = MCPMessage(
        sender="Main",
        receiver="RetrievalAgent",
        msg_type="retrieve",
        payload={"query": user_query}
    )
    msg5 = handle_retrieval_message(msg4)

    # Step 4: LLM Response
    msg6 = handle_llm_message(msg5)

    final_answer = msg6.payload["answer"]
    context_used = msg6.payload["context_used"]

    return final_answer, context_used
