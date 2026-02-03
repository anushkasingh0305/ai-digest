import requests

TELEGRAM_BOT_TOKEN = '8411332355:AAFtW2tvGJVbXRhtJU_46Q3Ihasp1eu545c'
TELEGRAM_CHAT_ID = 6614642154

print('Fetching real AI/Tech news from Hacker News...')

# Get top stories from Hacker News
top_stories = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json').json()[:50]

real_news = []
for story_id in top_stories:
    if len(real_news) >= 5:
        break
    story = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json').json()
    if story and 'title' in story and 'url' in story:
        real_news.append({
            'title': story.get('title', 'No title'),
            'url': story.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
            'score': story.get('score', 0),
            'comments': story.get('descendants', 0)
        })

print(f'\nFound {len(real_news)} real stories!\n')
print('=' * 60)

# Build message for Telegram
message_lines = [
    '━━━━━━━━━━━━━━━━━━━━━━━━━━',
    '🤖 𝗔𝗜 𝗗𝗶𝗴𝗲𝘀𝘁 - 𝗥𝗘𝗔𝗟 𝗡𝗘𝗪𝗦',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━',
    '📅 February 3, 2026',
    f'📊 {len(real_news)} Top Stories from Hacker News',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━',
    ''
]

for i, news in enumerate(real_news, 1):
    print(f'{i}. {news["title"]}')
    print(f'   🔼 {news["score"]} points | 💬 {news["comments"]} comments')
    print(f'   🔗 {news["url"]}')
    print()
    
    message_lines.append(f'📌 {i}. {news["title"]}')
    message_lines.append(f'🔼 {news["score"]} points | 💬 {news["comments"]} comments')
    message_lines.append(f'🔗 {news["url"]}')
    message_lines.append('')

message_lines.extend([
    '━━━━━━━━━━━━━━━━━━━━━━━━━━',
    '📋 QUICK LINKS:',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━',
])

for i, news in enumerate(real_news, 1):
    message_lines.append(f'{i}️⃣ {news["url"]}')

message_lines.extend([
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━',
    '✨ Powered by AI Digest Bot',
    '📰 Source: Hacker News',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━'
])

message = '\n'.join(message_lines)

print('=' * 60)
print('\nSending to Telegram...')

url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'disable_web_page_preview': True}
response = requests.post(url, json=payload, timeout=10)

if response.status_code == 200:
    print('✅ MESSAGE SENT SUCCESSFULLY TO TELEGRAM!')
else:
    print(f'❌ Error: {response.text}')
