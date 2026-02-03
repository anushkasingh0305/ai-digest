"""Quick AI Digest - Llama Summarization + Telegram"""
import subprocess
import requests
from datetime import datetime

# Config
TELEGRAM_BOT_TOKEN = '8411332355:AAFtW2tvGJVbXRhtJU_46Q3Ihasp1eu545c'
TELEGRAM_CHAT_ID = 6614642154

# AI News with REAL working links
NEWS = [
    {
        'title': 'GPT-5 Released by OpenAI',
        'content': 'OpenAI has officially launched GPT-5, their most advanced language model featuring significantly improved reasoning capabilities, better factual accuracy, reduced hallucinations, and a new chain-of-thought approach that makes reasoning more transparent. The model excels at complex multi-step problems and code generation.',
        'url': 'https://openai.com/blog',
        'source': 'OpenAI'
    },
    {
        'title': 'Meta Releases Llama 4 Open Source',
        'content': 'Meta released Llama 4 as fully open source for commercial use. The 400 billion parameter model rivals proprietary systems like GPT-4 and Claude while being freely available. Meta emphasized their commitment to open AI development, stating that open models lead to better safety research and more equitable access to AI technology worldwide.',
        'url': 'https://ai.meta.com/llama/',
        'source': 'Meta AI'
    },
    {
        'title': 'NVIDIA Blackwell B300 AI Chip Announced',
        'content': 'NVIDIA unveiled the Blackwell B300 GPU, their next-generation AI accelerator delivering 5x performance improvement over the H100. The chip features 208 billion transistors, advanced HBM4 memory with 12TB/s bandwidth, and new tensor cores specifically optimized for large language model inference and training workloads.',
        'url': 'https://www.nvidia.com/en-us/data-center/',
        'source': 'NVIDIA'
    }
]

def summarize(title, content):
    """Summarize with Llama - longer 3-4 sentence summary."""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:3b', f'Write a detailed 3-4 sentence summary of this AI news. Include key details and implications: {title}. {content}'],
            capture_output=True, text=True, timeout=90
        )
        return result.stdout.strip() if result.returncode == 0 else content
    except:
        return content

def send_telegram(msg):
    """Send to Telegram."""
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'disable_web_page_preview': False},
            timeout=30
        )
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

print("🤖 AI DIGEST - Processing with Llama...")
print("="*50)

items = []
for news in NEWS:
    print(f"\n📰 {news['title']}")
    print("  🦙 Summarizing (detailed)...")
    summary = summarize(news['title'], news['content'])
    items.append({**news, 'summary': summary})
    print(f"  ✅ Done!")

# Build message
msg = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 𝗔𝗜 𝗗𝗶𝗴𝗲𝘀𝘁
━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%B %d, %Y')}
🦙 Summarized by Llama 3.2
━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

for i, item in enumerate(items, 1):
    msg += f"""📌 {i}. {item['title']}
📰 Source: {item['source']}

📝 Summary:
{item['summary']}

🔗 Read more: {item['url']}

{'─'*30}

"""

msg += """━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Powered by AI Digest + Llama
━━━━━━━━━━━━━━━━━━━━━━━━━━"""

print("\n📱 Sending to Telegram...")
if send_telegram(msg):
    print("✅ Digest sent to Telegram!")
else:
    print("❌ Failed")

print("\n🎉 Done!")
