import worker
import time

start=time.time()
interval=30
while True:
  if time.time()>=interval+start:
    start=time.time()
    worker.worker_cycle()
