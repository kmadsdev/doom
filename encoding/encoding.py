import base64
import requests
from urllib.parse import quote, unquote

# ----------------------------------
# html -> base64, dataurl, hyperlink
# ----------------------------------

def html_to_base64(html: str) -> str:
    return base64.b64encode(html.encode("utf-8")).decode("utf-8")

def html_to_dataurl(html: str, mime="text/html") -> str:
    b64 = html_to_base64(html)
    return f"data:{mime};base64,{b64}"

def html_to_dataurl_encoded(html: str, mime="text/html") -> str:
    return f"data:{mime},{quote(html)}"

def html_to_hyperlink(html: str, mime="text/html") -> str:
    return html_to_dataurl(html, mime)

# ----------------------------------
# base64 -> html, dataurl, hyperlink
# ----------------------------------

def base64_to_html(b64: str) -> str:
    return base64.b64decode(b64.encode("utf-8")).decode("utf-8")

def base64_to_dataurl(b64: str, mime="text/html") -> str:
    return f"data:{mime};base64,{b64}"

def base64_to_hyperlink(b64: str, mime="text/html") -> str:
    return base64_to_dataurl(b64, mime)

# ----------------------------------
# dataurl -> html, base64, hyperlink
# ----------------------------------

def dataurl_to_base64(data_url: str) -> str:
    header, data = data_url.split(",", 1)
    if ";base64" not in header:
        raise ValueError("Not a base64 data URL")
    return data

def dataurl_to_html(data_url: str) -> str:
    header, data = data_url.split(",", 1)

    if ";base64" in header:
        return base64_to_html(data)
    else:
        return unquote(data)

def dataurl_to_hyperlink(data_url: str) -> str:
    return data_url  # already a hyperlink

# ----------------------------------
# hyperlink -> html, base64, dataurl
# ----------------------------------

def hyperlink_to_html(url: str) -> str:
    res = requests.get(url)
    res.raise_for_status()
    return res.text

def hyperlink_to_base64(url: str) -> str:
    html = hyperlink_to_html(url)
    return html_to_base64(html)

def hyperlink_to_dataurl(url: str, mime="text/html") -> str:
    html = hyperlink_to_html(url)
    return html_to_dataurl(html, mime)

def hyperlink_to_hyperlink(url: str, mime="text/html") -> str:
    return hyperlink_to_dataurl(url, mime)
