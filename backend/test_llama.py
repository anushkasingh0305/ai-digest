"""Test Llama summarization with Telegram"""
from scraper import summarize_with_llama, send_telegram, format_message

# Create sample digest items
items = [
    {
        'title': 'OpenAI GPT-5 Released with Major Improvements',
        'url': 'https://openai.com/gpt5',
        'summary': '',
        'source': 'Test',
        'points': 100
    },
    {
        'title': 'Google Gemini 2.0 Brings Multimodal AI to Everyone',
        'url': 'https://google.com/gemini',
        'summary': '',
        'source': 'Test',
        'points': 80
    }
]

print("🦙 Testing LOCAL Llama Summarization")
print("="*50)

# Summarize each item with Llama
for item in items:
    print(f"\n📰 {item['title']}")
    content = f"{item['title']} represents a significant advancement in artificial intelligence. The new model features improved reasoning capabilities, better code generation, and enhanced multimodal understanding."
    item['summary'] = summarize_with_llama(item['title'], content)
    print(f"   Summary: {item['summary']}")

# Format for Telegram
print("\n" + "="*50)
print("📱 Sending to Telegram...")
message = format_message(items)
result = send_telegram(message)
print(f"✅ Sent! Response: {result}")
