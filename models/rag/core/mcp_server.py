from fastmcp import FastMCP
from core.rag_agent import RAGAgent

# Initialize MCP
mcp = FastMCP("Hanzala-RAG-System")
agent = RAGAgent()

@mcp.tool()
def ask_my_knowledge_base(question: str) -> str:
    """
    Search into the Kafka-streamed Qdrant database and get 
    answers via Groq Llama-3.
    """
    return agent.generate(question)

if __name__ == "__main__":
    mcp.run()