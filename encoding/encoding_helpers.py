import base64
import gzip
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

# ----------------------------------
# file -> base64 dataurl txt
# ----------------------------------

def html_file_to_base64_dataurl(html_path: str, output_path: str = None) -> str:
    """
    Reads an HTML file, encodes it as a base64 data URL (text/html),
    optionally writes the URI to a .txt file, and returns the URI string.

    Compatible with JavaScript — the output can be used directly as
    an <a href> or window.location value in any modern browser.

    Args:
        html_path:   Path to the source .html file.
        output_path: Path for the output .txt file. If None, skips file write
                     and just returns the URI string.

    Returns:
        The full data URI string (potentially very large, up to 10+ MB).
    """
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    uri = html_to_dataurl(html, mime="text/html")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(uri)

    return uri

# ----------------------------------
# compressed html -> self-extracting data URL
# ----------------------------------

# Standalone HTML loader template with a pure-JS gzip decompressor
# (RFC 1951 + RFC 1952). Produces a .html file, not a data: URL.
#
# Why .html and not a data: URL:
#   Chrome enforces a ~2 MB navigation limit on data: URLs. Large payloads
#   (e.g. a full Doom bundle at ~2.4 MB gzipped) silently produce blank pages.
#   A .html file opened from disk (file://) has no such size limit, gets a
#   secure context, and Blob URLs work fine.
#
# How it works:
#   1. The payload (gzip bytes, base64-encoded) is embedded as a JS string.
#   2. A pure-JS inflate implementation decodes it in-browser.
#   3. The decompressed HTML bytes are wrapped in a Blob (text/html).
#   4. The page navigates to the Blob URL — the original HTML runs normally.
#
# __PAYLOAD__ is replaced at build time with the base64-encoded gzip bytes.
_COMPRESSED_LOADER_TEMPLATE = (
    '<!DOCTYPE html><meta charset="utf-8">'
    '<style>body{background:#111;color:#ccc;font:14px monospace;padding:2em}</style>'
    '<body><p id="s">Decompressing...</p><script>'
    '(function(){'
    'try{'
    # --- base64 decode ---
    'var $=atob("__PAYLOAD__");'
    'var b=new Uint8Array($.length);'
    'for(var i=0;i<$.length;i++)b[i]=$.charCodeAt(i);'
    # --- gzip header (RFC 1952) ---
    'var flg=b[3],p=10;'
    'if(flg&4)p+=(b[p]|b[p+1]<<8)+2;'
    'if(flg&8)while(b[p++]);'
    'if(flg&16)while(b[p++]);'
    'if(flg&2)p+=2;'
    # --- inflate (RFC 1951) ---
    'var sp=p*8;'
    'function rb(){var v=(b[sp>>3]>>(sp&7))&1;sp++;return v;}'
    'function rn(n){var v=0;for(var i=0;i<n;i++)v|=rb()<<i;return v;}'
    'function mh(ls,n){'
      'var c=new Uint16Array(16),f=new Uint16Array(16),m={};'
      'for(var i=0;i<n;i++)if(ls[i])c[ls[i]]++;'
      'var x=0;for(var i=1;i<16;i++){x=(x+c[i-1])<<1;f[i]=x;}'
      'for(var i=0;i<n;i++)if(ls[i])m[ls[i]*65536+f[ls[i]]++]=i;'
      'return m;'
    '}'
    'function rs(m){'
      'var code=0;'
      'for(var l=1;l<=15;l++){code=code<<1|rb();var k=l*65536+code;if(k in m)return m[k];}'
      'throw new Error("bad huffman code");'
    '}'
    'var LB=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258];'
    'var LE=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0];'
    'var DB=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577];'
    'var DE=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];'
    'var iz=((b[b.length-4])|(b[b.length-3]<<8)|(b[b.length-2]<<16)|(b[b.length-1]<<24))>>>0;'
    'var out=new Uint8Array(iz>0&&iz<268435456?iz:1048576),ol=0;'
    'function em(v){if(ol>=out.length){var t=new Uint8Array(ol*2);t.set(out);out=t;}out[ol++]=v;}'
    'var fin;'
    'do{'
      'fin=rb();var bt=rn(2);'
      'if(bt===0){'
        'sp=(sp+7)&~7;var bp=sp>>3;var bl=b[bp]|b[bp+1]<<8;'
        'sp=(bp+4)*8;'
        'for(var i=0;i<bl;i++)em(b[(sp>>3)+i]);'
        'sp+=bl*8;'
      '}else{'
        'var lm,dm;'
        'if(bt===1){'
          'var fl=new Uint8Array(288),fd=new Uint8Array(32);'
          'for(var i=0;i<144;i++)fl[i]=8;for(var i=144;i<256;i++)fl[i]=9;'
          'for(var i=256;i<280;i++)fl[i]=7;for(var i=280;i<288;i++)fl[i]=8;'
          'for(var i=0;i<32;i++)fd[i]=5;'
          'lm=mh(fl,288);dm=mh(fd,32);'
        '}else{'
          'var hl=rn(5)+257,hd=rn(5)+1,hc=rn(4)+4;'
          'var co=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];'
          'var cl=new Uint8Array(19);'
          'for(var i=0;i<hc;i++)cl[co[i]]=rn(3);'
          'var cm=mh(cl,19);'
          'var al=new Uint8Array(hl+hd);'
          'for(var i=0;i<hl+hd;){'
            'var cs=rs(cm);'
            'if(cs<16)al[i++]=cs;'
            'else if(cs===16){var r=rn(2)+3,v=al[i-1];while(r--)al[i++]=v;}'
            'else if(cs===17){var r=rn(3)+3;while(r--)al[i++]=0;}'
            'else{var r=rn(7)+11;while(r--)al[i++]=0;}'
          '}'
          'lm=mh(al,hl);dm=mh(al.subarray(hl),hd);'
        '}'
        'for(;;){'
          'var s=rs(lm);'
          'if(s<256)em(s);'
          'else if(s===256)break;'
          'else{'
            'var li=s-257,ln=LB[li]+rn(LE[li]),di=rs(dm),d=DB[di]+rn(DE[di]),st=ol-d;'
            'for(var i=0;i<ln;i++)em(out[st+i]);'
          '}'
        '}'
      '}'
    '}while(!fin);'
    # navigate to Blob URL — no data: URL size limit
    'var blob=new Blob([out.subarray(0,ol)],{type:"text/html"});'
    'location.replace(URL.createObjectURL(blob));'
    '}catch(e){document.getElementById("s").textContent="Decode error: "+(e&&e.message||e);}'
    '})()'
    '</script>'
)


def gzip_compress(data: bytes, level: int = 9) -> bytes:
    """Compress bytes with gzip at the given compression level (0-9)."""
    return gzip.compress(data, compresslevel=level)


def html_to_compressed_html(html: str, level: int = 9) -> str:
    """
    Compress an HTML string with gzip and return a standalone self-extracting
    HTML page that decompresses and renders the original on load.

    The output is a .html file, not a data: URL. Chrome limits data: URL
    navigation to ~2 MB; large payloads require a Blob URL, which in turn
    requires the page to have a real origin — satisfied by file:// or http://.

    The loader is fully offline: no network requests at any time. It uses
    a pure-JS DEFLATE inflate (RFC 1951) + gzip header parser (RFC 1952),
    then hands the decompressed bytes to a Blob URL via location.replace().

    Args:
        html:  The full HTML source to compress.
        level: gzip compression level (0 = none, 9 = best). Default 9.

    Returns:
        The full standalone loader HTML as a string.
    """
    compressed = gzip_compress(html.encode("utf-8"), level)
    payload_b64 = base64.b64encode(compressed).decode("ascii")
    return _COMPRESSED_LOADER_TEMPLATE.replace("__PAYLOAD__", payload_b64)


def html_file_to_compressed_html(html_path: str, output_path: str = None) -> str:
    """
    Reads an HTML file, compresses it with gzip, and returns a standalone
    self-extracting HTML string that decompresses on load.

    Optionally writes the result to an output .html file.

    Args:
        html_path:   Path to the source .html file.
        output_path: Path for the output .html file. If None, skips file write.

    Returns:
        The full standalone loader HTML as a string.
    """
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    loader = html_to_compressed_html(html)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(loader)

    return loader


# Keep old name as alias for compatibility
html_to_compressed_dataurl = html_to_compressed_html
html_file_to_compressed_dataurl = html_file_to_compressed_html
