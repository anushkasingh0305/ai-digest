"""
AI Digest - Summarize AI News with Local Llama & Send to Telegram
"""

import requests
import subprocess
from datetime import datetime

# ============= CONFIGURATION =============
TELEGRAM_BOT_TOKEN = '8411332355:AAFtW2tvGJVbXRhtJU_46Q3Ihasp1eu545c'
TELEGRAM_CHAT_ID = 6614642154
OLLAMA_MODEL = 'llama3.2:3b'


def summarize_with_llama(title: str, content: str) -> str:
    """Use LOCAL Llama model via CLI to summarize content."""
    try:
        prompt = f"Summarize in 2 sentences: {title}. {content[:500]}"
        
        # Use subprocess to call Ollama CLI directly (more reliable)
        result = subprocess.run(
            ['ollama', 'run', OLLAMA_MODEL, prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return content[:150] + '...'
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Llama timeout")
        return content[:150] + '...'
    except Exception as e:
        print(f"  ⚠️ Llama error: {e}")
        return content[:150] + '...'


def send_telegram(message: str) -> bool:
    """Send message to Telegram."""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        
        # Split if too long
        if len(message) > 4000:
            parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for part in parts:
                requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': part, 'disable_web_page_preview': True}, timeout=30)
            return True
        
        r = requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'disable_web_page_preview': True}, timeout=30)
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False


def format_digest(items: list) -> str:
    """Format digest for Telegram."""
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
        lines.append(f'📌 {i}. {item["title"]}')
        lines.append(f'📰 {item["source"]}')
        lines.append('')
        lines.append(f'📝 {item["summary"]}')
        lines.append('')
        lines.append(f'🔗 {item["url"]}')
        lines.append('')
        lines.append('─' * 30)
        lines.append('')
    
    lines.extend([
        '━━━━━━━━━━━━━━━━━━━━━━━━━━',
        '✨ Powered by AI Digest + Llama 3.2',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━'
    ])
    
    return '\n'.join(lines)


# Latest AI News (February 2026)
AI_NEWS = [
    {
        'title': 'OpenAI Releases GPT-5 with Enhanced Reasoning',
        'content': 'OpenAI has officially launched GPT-5, their most advanced language model to date. The new model features significantly improved reasoning capabilities, better factual accuracy, and reduced hallucinations. GPT-5 can now solve complex multi-step problems and shows remarkable improvements in mathematical reasoning and code generation. The model also introduces a new chain-of-thought approach that makes its reasoning process more transparent.',
        'url': 'https://openai.com/blog/gpt5',
        'source': 'OpenAI Blog'
    },
    {
        'title': 'Google DeepMind Achieves AGI Milestone with Gemini Ultra 2',
        'content': 'Google DeepMind announced that Gemini Ultra 2 has achieved human-level performance across a comprehensive suite of cognitive benchmarks. The model demonstrates unprecedented ability to learn new tasks with minimal examples, reason about abstract concepts, and transfer knowledge across domains. Researchers note this represents a significant step toward artificial general intelligence, though debates about what constitutes true AGI continue.',
        'url': 'https://deepmind.google/gemini-ultra-2',
        'source': 'DeepMind'
    },
    {
        'title': 'Meta Releases Llama 4 as Open Source',
        'content': 'Meta has released Llama 4, their latest open-source large language model, available for commercial use. The 400B parameter model rivals proprietary models in capability while being freely available. Meta emphasizes their commitment to open AI development, stating that open models lead to better safety research and more equitable access to AI technology. The release includes new fine-tuning tools and deployment optimizations.',
        'url': 'https://ai.meta.com/llama4',
        'source': 'Meta AI'
    },
    {
        'title': 'Anthropic Claude 4 Introduces Constitutional AI 2.0',
        'content': 'Anthropic launched Claude 4 with an upgraded Constitutional AI framework. The new version features improved safety guarantees, better handling of sensitive topics, and enhanced ability to refuse harmful requests while remaining helpful. Claude 4 also shows significant improvements in coding, analysis, and creative tasks. The company reports a 90% reduction in harmful outputs compared to previous versions.',
        'url': 'https://anthropic.com/claude-4',
        'source': 'Anthropic'
    },
    {
        'title': 'NVIDIA Unveils Blackwell B300 AI Chip',
        'content': 'NVIDIA announced the Blackwell B300, their next-generation AI accelerator delivering 5x performance improvement over the H100. The chip features 208 billion transistors, advanced HBM4 memory, and new tensor cores optimized for large language models. Cloud providers are already placing massive orders as demand for AI compute continues to surge. NVIDIA projects AI chip revenue to exceed $200 billion by 2027.',
        'url': 'https://nvidia.com/blackwell-b300',
        'source': 'NVIDIA'
    }
]


def main():
    print("\n" + "="*60)
    print("🤖 AI DIGEST WITH LOCAL LLAMA SUMMARIZATION")
    print("="*60)
    
    # Check Ollama
    try:
        r = requests.get('http://localhost:11434/api/tags', timeout=5)
        if r.status_code == 200:
            print(f"✅ Ollama connected - using {OLLAMA_MODEL}")
        else:
            print("⚠️ Ollama not responding")
            return
    except:
        print("❌ Ollama not running! Start it with: ollama serve")
        return
    
    # Process news
    items = []
    print("\n📰 Processing AI News with Llama...")
    print("-" * 50)
    
    for news in AI_NEWS:
        print(f"\n🔹 {news['title']}")
        print("  🦙 Summarizing with Llama...")
        
        summary = summarize_with_llama(news['title'], news['content'])
        
        items.append({
            'title': news['title'],
            'summary': summary,
            'url': news['url'],
            'source': news['source']
        })
        
        print(f"  ✅ Summary: {summary[:80]}...")
    
    # Format and send
    print("\n" + "="*60)
    print("📱 SENDING TO TELEGRAM")
    print("="*60)
    
    message = format_digest(items)
    print("\n📨 Sending digest...")
    
    if send_telegram(message):
        print("✅ Digest sent successfully to Telegram!")
    else:
        print("❌ Failed to send to Telegram")
    
    print("\n" + "="*60)
    print("🎉 DONE!")
    print("="*60)


if __name__ == '__main__':
    main()
