"""
AI Digest Web Scraper with Llama Summarization
Fetches real AI/ML news and uses LOCAL Ollama Llama model to summarize content
Output format: Title, Summary, Link
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
import hashlib
import subprocess

# ============= CONFIGURATION =============
TELEGRAM_BOT_TOKEN = '8411332355:AAFtW2tvGJVbXRhtJU_46Q3Ihasp1eu545c'
TELEGRAM_CHAT_ID = 6614642154

# Local Ollama model
OLLAMA_MODEL = 'llama3.2:3b'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def summarize_with_llama(title: str, content: str) -> str:
    """Use LOCAL Llama model via Ollama to summarize content."""
    
    if not content or len(content) < 50:
        return content[:150] + '...' if content else title
    
    try:
        prompt = f"Summarize in 2-3 sentences: {title}. {content[:1500]}"
        
        # Call Ollama API (runs locally on port 11434)
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,
                    'num_predict': 150
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('response', '').strip()
            return summary if summary else content[:150] + '...'
        else:
            print(f"  ⚠️ Ollama API error: {response.status_code}")
            return content[:150] + '...'
        
    except Exception as e:
        print(f"  ⚠️ Llama summarization failed: {e}")
        return content[:150] + '...' if content else title


def fallback_summarize(content: str, max_length: int = 150) -> str:
    """Fallback summarization without LLM."""
    if not content:
        return ''
    
    # Clean and truncate
    content = re.sub(r'\s+', ' ', content).strip()
    
    # Try to get first complete sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    summary = ''
    for sentence in sentences:
        if len(summary) + len(sentence) < max_length:
            summary += sentence + ' '
        else:
            break
    
    return summary.strip() if summary else content[:max_length] + '...'


def generate_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def fetch_url_content(url: str, max_length: int = 1500) -> str:
    """Fetch and extract main content from a URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for el in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            el.decompose()
        
        # Try to find main content
        content = ''
        for selector in ['article', 'main', '.post-content', '.article-body', '.content', 'p']:
            elements = soup.select(selector)
            if elements:
                texts = [el.get_text(strip=True) for el in elements[:10]]
                content = ' '.join(texts)
                if len(content) > 100:
                    break
        
        if not content:
            content = soup.get_text(strip=True)
        
        # Clean up
        content = re.sub(r'\s+', ' ', content).strip()
        return content[:max_length]
        
    except Exception as e:
        return ''


def scrape_hackernews(limit: int = 5) -> List[Dict]:
    """Scrape top stories from Hacker News API."""
    print("\n📰 Fetching from Hacker News...")
    items = []
    
    try:
        top_ids = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json', timeout=5).json()[:25]
        
        for story_id in top_ids:
            if len(items) >= limit:
                break
            
            try:
                story = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json', timeout=5).json()
                
                if not story or 'title' not in story or 'url' not in story:
                    continue
                
                title = story['title']
                url = story['url']
                
                print(f"  Fetching: {title[:40]}...")
                
                # Fetch full content from the URL
                content = fetch_url_content(url)
                
                # Summarize with Llama
                if groq_client and content:
                    print(f"    🦙 Summarizing with Llama...")
                    summary = summarize_with_llama(title, content)
                else:
                    summary = fallback_summarize(content)
                
                items.append({
                    'title': title,
                    'summary': summary,
                    'url': url,
                    'source': 'Hacker News',
                    'points': story.get('score', 0)
                })
                print(f"  ✓ Done")
                
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"  ❌ HN Error: {e}")
    
    return items


def scrape_reddit(limit: int = 4) -> List[Dict]:
    """Scrape from Reddit ML communities."""
    print("\n🤖 Fetching from Reddit...")
    items = []
    subreddits = ['MachineLearning', 'artificial', 'LocalLLaMA']
    
    for sub in subreddits:
        if len(items) >= limit:
            break
        try:
            url = f'https://www.reddit.com/r/{sub}/hot.json?limit=8'
            response = requests.get(url, headers=HEADERS, timeout=5)
            data = response.json()
            
            for post in data.get('data', {}).get('children', []):
                if len(items) >= limit:
                    break
                
                p = post.get('data', {})
                if p.get('stickied') or p.get('score', 0) < 5:
                    continue
                
                title = p.get('title', '')
                post_url = p.get('url', '')
                selftext = p.get('selftext', '')
                permalink = f"https://reddit.com{p.get('permalink', '')}"
                
                print(f"  Fetching: r/{sub} - {title[:35]}...")
                
                # Get content
                if selftext:
                    content = selftext[:1500]
                elif post_url and 'reddit.com' not in post_url:
                    content = fetch_url_content(post_url)
                else:
                    content = title
                
                # Summarize with Llama
                if groq_client and content and len(content) > 50:
                    print(f"    🦙 Summarizing with Llama...")
                    summary = summarize_with_llama(title, content)
                else:
                    summary = fallback_summarize(content)
                
                final_url = post_url if post_url and 'reddit.com' not in post_url else permalink
                
                items.append({
                    'title': title,
                    'summary': summary,
                    'url': final_url,
                    'source': f'r/{sub}',
                    'points': p.get('score', 0)
                })
                print(f"  ✓ Done")
                
        except Exception as e:
            print(f"  ❌ Reddit Error ({sub}): {e}")
    
    return items


def scrape_all() -> List[Dict]:
    """Scrape all sources."""
    print("\n" + "="*60)
    print("🚀 AI DIGEST SCRAPER WITH LOCAL LLAMA")
    print("="*60)
    
    # Check Ollama connection
    try:
        resp = requests.get('http://localhost:11434/api/tags', timeout=5)
        if resp.status_code == 200:
            print(f"✅ Ollama connected - using {OLLAMA_MODEL}")
        else:
            print("⚠️ Ollama not responding - using fallback summarization")
    except:
        print("⚠️ Ollama not running - using fallback summarization")
    
    all_items = []
    
    # Scrape sources
    all_items.extend(scrape_hackernews(limit=5))
    all_items.extend(scrape_reddit(limit=4))
    
    # Remove duplicates and sort by points
    seen = set()
    unique = []
    for item in all_items:
        if item['url'] not in seen:
            seen.add(item['url'])
            unique.append(item)
    
    unique.sort(key=lambda x: x.get('points', 0), reverse=True)
    
    print(f"\n✅ Total items: {len(unique)}")
    return unique


def format_message(items: List[Dict]) -> str:
    """Format as Title, Summary, Link for Telegram."""
    lines = [
        '━━━━━━━━━━━━━━━━━━━━━━━━━━',
        '🤖 𝗔𝗜 𝗗𝗶𝗴𝗲𝘀𝘁',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━',
        f'📅 {datetime.now().strftime("%B %d, %Y")}',
        f'📊 {len(items)} Stories | 🦙 Llama Summarized',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━',
        ''
    ]
    
    for i, item in enumerate(items, 1):
        # Title
        lines.append(f'📌 {i}. {item["title"]}')
        lines.append(f'📰 {item["source"]}')
        lines.append('')
        
        # Summary
        lines.append(f'📝 {item["summary"]}')
        lines.append('')
        
        # Link
        lines.append(f'🔗 {item["url"]}')
        lines.append('')
        lines.append('─' * 30)
        lines.append('')
    
    lines.extend([
        '━━━━━━━━━━━━━━━━━━━━━━━━━━',
        '✨ Powered by AI Digest + Llama',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━'
    ])
    
    return '\n'.join(lines)


def send_telegram(message: str) -> bool:
    """Send to Telegram."""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        
        # Split if too long (Telegram limit is 4096)
        if len(message) > 4000:
            parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for part in parts:
                requests.post(url, json={
                    'chat_id': TELEGRAM_CHAT_ID, 
                    'text': part, 
                    'disable_web_page_preview': True
                }, timeout=10)
            return True
        
        r = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID, 
            'text': message, 
            'disable_web_page_preview': True
        }, timeout=10)
        return r.status_code == 200
        
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False


def main():
    """Run scraper and send to Telegram."""
    items = scrape_all()
    
    if not items:
        print("❌ No items found!")
        return
    
    message = format_message(items)
    
    print("\n" + "="*60)
    print("📨 MESSAGE PREVIEW (Title, Summary, Link format):")
    print("="*60)
    print(message)
    print("="*60)
    
    print("\n📤 Sending to Telegram...")
    if send_telegram(message):
        print("✅ SENT SUCCESSFULLY! Check your Telegram!")
    else:
        print("❌ Failed to send")
    
    return items


if __name__ == '__main__':
    main()
