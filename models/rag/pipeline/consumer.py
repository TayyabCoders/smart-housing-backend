from confluent_kafka import Consumer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import json

# 1. Models aur Clients Initialize karna
model = SentenceTransformer('all-MiniLM-L6-v2') # Chota aur fast model
qdrant = QdrantClient("localhost", port=6333)
collection_name = "pro_rag_collection"

client = QdrantClient(
    url="YOUR_CLOUD_ENDPOINT", 
    api_key="YOUR_API_KEY"
)

# 2. Kafka Consumer Setup
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'rag-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(conf)
consumer.subscribe(['rag-data-topic'])

print("Consumer started... Waiting for data from Kafka.")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        # Data mil gaya
        data = json.loads(msg.value().decode('utf-8'))
        text_content = data['content']
        
        print(f"Processing: {text_content}")

        # Vector (Embedding) banana
        vector = model.encode(text_content).tolist()

        # Qdrant mein save karna
        qdrant.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=data['id'],
                    vector=vector,
                    payload={"text": text_content, "metadata": data['metadata']}
                )
            ]
        )
        print(f"Successfully stored in Qdrant!")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()