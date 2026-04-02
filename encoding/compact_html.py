import re
from datetime import datetime


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f: return f.read()
def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f: f.write(content)


def inline_css(html: str, css: str) -> str:
    pattern = r'<link\s+rel=["\']stylesheet["\']\s+href=["\']style\.css["\']\s*>'
    replacement = f"<style>\n{css}\n</style>"
    return re.sub(pattern, replacement, html, flags=re.IGNORECASE)
def inline_js(html: str, js: str) -> str:
    pattern = r'<script\s+src=["\']script\.js["\']\s*>\s*</script>'
    replacement = f"<script>\n{js}\n</script>"
    return re.sub(pattern, replacement, html, flags=re.IGNORECASE)


def bundle_html(index_path="index.html", css_path="style.css", js_path="script.js") -> str:
    html = read_file(index_path)
    css = read_file(css_path)
    js = read_file(js_path)

    html = inline_css(html, css)
    html = inline_js(html, js)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_name = f"source_{timestamp}.html"

    write_file(output_name, html)
    return output_name


if __name__ == "__main__":
    output_file = bundle_html()
    print(f"✅ Generated: {output_file}")
