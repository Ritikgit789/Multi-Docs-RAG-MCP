# main.py

from core_mcp.mcp import MCPMessage
from agents.ingestion_agent import run_ingestion_agent

def test_mcp_message():
    # Simulate IngestionAgent sending chunks to IndexAgent
    chunks = [
        "Slide 1: Revenue increased by 20%",
        "Slide 2: Customer churn dropped by 5%"
    ]
    embeddings = [
        [0.1, 0.2, 0.3],  # Example embedding vectors
        [0.4, 0.5, 0.6]
    ]

    message = MCPMessage(
        sender="IngestionAgent",
        receiver="IndexAgent",
        msg_type=MCPMessage.TYPE_INDEX,
        payload={
            "chunks": chunks,
            "embeddings": embeddings,
            "source_file": "sales_review.pptx"
        }
    )

    print("✅ Generated MCP Message (IngestionAgent → IndexAgent):")
    print(message.to_json())

# if __name__ == "__main__":
#     test_mcp_message()

if __name__ == "__main__":
    file_path = "documents/doc.txt"  # put any supported file here
    message = run_ingestion_agent(file_path, receiver_agent="IndexAgent")
    print("✅ Generated MCP Message (IngestionAgent → IndexAgent):")
    print(message.to_json())