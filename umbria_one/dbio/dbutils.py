#
import time
import asyncio


#


#
from umbria_one.dbio.dbio import save_live_and_history_batch


#
async def history_worker(
    history_queue,
    batch_size = 100,
    batch_timeout = 5.0,
):

    print("WORKER: Started and watching queue...")

    while True:
        batch = []
        start_time = time.time()

        while len(batch) < batch_size:
            time_left = batch_timeout - (time.time() - start_time)

            try:

                item = await asyncio.wait_for(history_queue.get(), timeout=max(0, time_left))
                batch.append(item)

            except asyncio.TimeoutError:

                break

        if batch:

            try:

                await save_live_and_history_batch(batch)

            except Exception as e:
                print(f"WORKER ERROR during save: {e}")
            finally:
                for _ in range(len(batch)):
                    history_queue.task_done()
