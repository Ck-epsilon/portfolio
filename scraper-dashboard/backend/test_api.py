import httpx, asyncio, json

async def test():
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get('http://localhost:8700/health')
        print('Health:', r.json())

        r = await c.post('http://localhost:8700/tasks', json={
            'url': 'https://books.toscrape.com',
            'config': {'selector': 'article.product_pod', 'max_pages': 1}
        })
        task = r.json()
        print(f'Task: {task["id"]} status={task["status"]}')

        for i in range(15):
            await asyncio.sleep(1)
            r = await c.get(f'http://localhost:8700/tasks/{task["id"]}')
            t = r.json()
            print(f'  {i}s: {t["status"]} rows={t.get("rows_scraped",0)} pages={t.get("pages_scraped",0)}')
            if t['status'] in ('completed','failed'):
                break

        r = await c.get('http://localhost:8700/tasks')
        print(f'All tasks: {len(r.json())}')

        r = await c.get(f'http://localhost:8700/tasks/{task["id"]}/export')
        lines = r.text.strip().split('\n')
        print(f'CSV: {len(lines)} lines, header: {lines[0]}')

asyncio.run(test())
