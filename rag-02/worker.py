import redis 
import ast 

# SETUP THE CONNECTION TO REDIS

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

while True:
    queue_name, raw_payload = redis_client.blpop("rag:requests")
    payload = ast.literal_eval(raw_payload)
    job_id = payload['job_id']
    query = payload['query']
    print(f"Processing Job {job_id}")
    print(query)