import asyncio, sys
from task_queue import Task, TaskManager, TaskStatus
from scraper import scrape_task

async def test():
    task = Task(
        url='https://books.toscrape.com',
        config={'selector': 'article.product_pod', 'max_pages': 1}
    )
    task.status = TaskStatus.RUNNING
    print(f'Starting scrape: {task.id}')

    # Collect log messages
    log_task = asyncio.create_task(_log_collector(task))

    try:
        await asyncio.wait_for(scrape_task(task), timeout=20)
        print(f'Done: status={task.status}, rows={len(task.results)}')
    except asyncio.TimeoutError:
        print('TIMEOUT - scraper hung')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

    log_task.cancel()

async def _log_collector(task):
    while True:
        try:
            msg = await asyncio.wait_for(task.log_queue.get(), timeout=0.5)
            print(f'  [{msg.get("type","")}] {msg.get("message","")[:80]}')
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break

asyncio.run(test())
