def format_digest_text(digest: dict) -> str:
    parts = []
    items = digest.get('items', [])
    parts.append(f"Digest — {len(items)} items\n")
    for i, it in enumerate(items, 1):
        title = it.get('title') or it.get('text','(no title)')
        url = it.get('url','')
        parts.append(f"{i}. {title}\n{url}\n")
    return "\n".join(parts)


def format_digest_html(digest: dict) -> str:
        items = digest.get('items', [])
        rows = []
        for i, it in enumerate(items, 1):
                title = (it.get('title') or it.get('text','(no title)')).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                url = it.get('url','')
                if url:
                        rows.append(f"<li><a href=\"{url}\">{title}</a></li>")
                else:
                        rows.append(f"<li>{title}</li>")

        html = f"""
<html>
    <head><meta charset="utf-8"><title>AI Digest</title></head>
    <body>
        <h1>AI Digest — {len(items)} items</h1>
        <ul>
            {''.join(rows)}
        </ul>
    </body>
</html>
"""
        return html
