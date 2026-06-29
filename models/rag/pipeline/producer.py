from confluent_kafka import Producer
import json
import time

# Kafka Config
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def stream_text_data(topic, text_list):
    for i, text in enumerate(text_list):
        data = {
            "id": i,
            "content": text,
            "metadata": {"source": "manual_entry", "timestamp": time.time()}
        }
        # Data ko JSON bana kar bhej rahe hain
        producer.produce(topic, json.dumps(data).encode('utf-8'), callback=delivery_report)
        print(f"Sending: {text}")
    
    producer.flush()

if __name__ == "__main__":
    my_data = [
        "Redis is an in-memory data store used for caching.",
        "Qdrant is a vector database optimized for AI search.",
        "Kafka is a distributed streaming platform for real-time data."
    ]
    stream_text_data('rag-data-topic', my_data)