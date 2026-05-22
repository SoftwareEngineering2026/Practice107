import os
from redis import Redis
from rq import Worker, Queue


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "text_tasks")


def main():
    redis_conn = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=False
    )

    queue = Queue(QUEUE_NAME, connection=redis_conn)

    worker = Worker(
        queues=[queue],
        connection=redis_conn
    )

    print("Worker started")
    print(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"Queue: {QUEUE_NAME}")

    worker.work()


if __name__ == "__main__":
    main()