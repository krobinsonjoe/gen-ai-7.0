import uuid 
import redis

# SETUP THE CONNECTION TO REDIS

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# GENERATE PAYLOAD AND SEND TO REDIS 

def store_query(query):
    job_id = str(uuid.uuid4())
    payload = {
        "job_id": job_id,
        "query": query
    }
    redis_client.rpush("rag:requests",str(payload))
    return job_id

user_query = input("Human Question: ")
job = store_query(user_query)

print("QUERY SENT TO QUEUE SUCCESSFULLY")
print(job)