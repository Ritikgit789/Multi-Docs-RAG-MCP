# main.py --- It is the main file that runs the RAG pipeline with the help of the agents and integration of MCP

# Importing the necessary modules
from core_mcp.mcp import MCPMessage
from agents.ingestion_agent import run_ingestion_agent
from agents.indexagent import handle_index_message
from agents.retrieval_agent import handle_retrieval_message
from agents.llmresponse_agent import handle_llm_message

# Step 1: Define initial message
msg1 = MCPMessage(
    sender="Main",
    receiver="IngestionAgent",
    msg_type="ingest",
    payload={
        "file_path": "D:/SLRIS/documents/NIPS-2017-attention-is-all-you-need-Paper.pdf",
        "doc_type": "pdf"
    }
)

#  Step 2: Ingestion Agent (uses file_path from msg1)
msg2 = run_ingestion_agent(msg1.payload["file_path"])  # no hardcoding again

#  Step 3: Indexing
msg3 = handle_index_message(msg2)

#  Step 4: Retrieval
msg4 = MCPMessage(
    sender="Main",
    receiver="RetrievalAgent",
    msg_type="retrieve",
    payload={
        "query": "What is self-attention mechanism?"
    }
)
msg5 = handle_retrieval_message(msg4)

#  Step 5: LLM Response
msg6 = handle_llm_message(msg5)

# Final Output
print("\n Final Answer:\n", msg6.payload["answer"])
