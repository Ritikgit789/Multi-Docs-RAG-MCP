import json
from utils.llm_call import call_llm_gemini
from core_mcp.mcp import MCPMessage  # Make sure this is imported

def handle_llm_message(mcp_message):
    payload = mcp_message["payload"]  # FIXED: class property
    context_chunks = payload["retrieved_context"]
    query = payload["query"]
    trace_id = mcp_message["trace_id"]

    # Combine context
    context_text = "\n\n".join(context_chunks)

    # Strong Prompt
    prompt = f"""
You are a focused and concise assistant, you can answer like an analyst, student, teacher, daat scientist, salesman and more

Strictly follow these instructions:
- Use only the information provided in the retrieved context below. Do not hallucinate or make assumptions.
- Give good, structured and concise answers.
- Give more detailed long answers at depth concept questions according to the context.
- If any answer from documents is short, use your some own knowledge to expand the answer.
- Don't use slash n (new line) in your answer.
- Do not be vague or generic. Provide specific and relevant answers only.
- Maintain a professional, analytical tone in your response.
- Do not repeat the context or query.
- If the context is insufficient to answer, reply: "Not enough information in retrieved data."

### Retrieved Context:
{context_text}

### User Query:
{query}

### Your Answer:
"""

    # Call Gemini
    answer = call_llm_gemini(prompt)

    # Return MCP message
    response_msg = MCPMessage(
        sender="LLMResponseAgent",
        receiver="CoordinatorAgent",
        msg_type="LLM_RESPONSE",
        trace_id=trace_id,
        payload={
            "answer": answer.strip(),
            "context_used": context_chunks,
            "query": query
        }
    )

    print("\n LLMResponseAgent → CoordinatorAgent MCP Message:")
    print(json.dumps(response_msg.to_dict(), indent=2))  # FIXED: use response_msg, not mcp_message

    return response_msg  # FIXED: must return for chaining


# Optional dev test block
if __name__ == "__main__":
    test_message = {
        "type": "RETRIEVAL_RESULT",
        "sender": "RetrievalAgent",
        "receiver": "LLMResponseAgent",
        "trace_id": "test-trace-002",
        "payload": {
            "retrieved_context": [
                "Encoder and Decoder Stacks\nEncoder:\nThe encoder is composed of a stack of N = 6 identical layers",
                "The best performing models also connect the encoder and decoder through an attention mechanism",
                "In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack"
            ],
            "query": "What is the encoder-decoder architecture, describe it in detail?"
        }
    }
    handle_llm_message(test_message)
