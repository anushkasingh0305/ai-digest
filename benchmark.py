import argparse
import time
from src.tools.adapters_placeholder import PlaceholderAdapter

async def run_embedding(count: int):
    adapter = PlaceholderAdapter()
    items = await adapter.fetch_items()
    start = time.time()
    # mock embedding work
    for i in range(count):
        _ = hash(items[0]['text'])
    dur = time.time() - start
    print(f"Mock embedded {count} items in {dur:.3f}s")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['embedding','dedup','full'], default='full')
    parser.add_argument('--count', type=int, default=200)
    args = parser.parse_args()
    import asyncio
    if args.mode == 'embedding':
        asyncio.run(run_embedding(args.count))
    else:
        asyncio.run(run_embedding(args.count))
