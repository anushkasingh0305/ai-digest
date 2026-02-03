import asyncio
from typing import List

class PlaceholderAdapter:
    async def fetch_items(self, hours: int = 24) -> List[dict]:
        await asyncio.sleep(0.01)
        return [
            {
                'id': 'placeholder-1',
                'title': 'Test item: AI digest scaffold',
                'url': 'https://example.com',
                'text': 'This is a placeholder item for testing the pipeline.'
            }
        ]
