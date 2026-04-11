# DOOM OFFLINE

**Zero files. Zero hosting. Just pure DOOM - into the URL.**
> **Website: [https://kmads.dev/doom](https://kmads.dev/doom)**

An offline web application that packs the original **DOOM** (1993) + an self-made additional handcrafted **MicroDOOM** (compact version / remake) into single HTML file. <br>
Then encodes them as **base64 data URIs** that you can paste into any browser and play - fully plug-and-play offline games, no backend or files required.

There are two modes for each game:
- Play Online - the game will run on our servers, not multiplayer (yet)
- Play Offline - the game will run on your own browser - just save the special URL as bookmark


<br>


## What Is This?

This project explores how far you can push browser encoding and compression by cramming entire playable games into a single URI string. For science brothers.

| Game               | Raw HTML  | Rendered Size  | Description |
|--------------------|-----------|----------------|-------------|
| **DOOM**           | ~7 MB     | ~4.4 MB (gzip) | id Software's 1993 classic compiled to WebAssembly, bundled with `doom1.wad` (shareware) and a JS runtime shim - all inline |
| **MicroDOOM v1.0** | ~44 KB    | ~44 KB | A DOOM-like raycasting FPS written from scratch in vanilla JS. Enemies, weapons, HUD - smaller than a favicon |
| **MicroDOOM v1.1** | ~50-60 KB | ~50-60 KB | Improved version with additional features (WIP) |


<br>


## Why?

For the sake of science. This project exists to stress-test encoding and compression at the browser level - seeing what happens when you shove an entire FPS into as URI. No special purpose. Just fun.


<br>


### The Trick

Here's the thing: browser can only support Data URIs with up to 8MB (on the best case scenarios), but on most cases browser only render 1-4MB of data before crashing or stopping. 

The workaround for this was very simple: the URI should be compressed, then the user's own browser would do the rest of the trick - they uncompressed the URI in real time, as the user plays the game - it uses gzip, an open-source file compression program and format.

> Note: Chrome already has Gzip built-in in order to make websites load faster. 
Others use it to decompress images, styles or short scripts, we are use it to decompress THE WHOLE WEBSITE PAGE.


<br>


### Requirements

| Tool                     | Browser | Version |
|--------------------------|---------|---------|
| Gzip DecompressionStream | Chrome  | 80+     |
| Gzip DecompressionStream | Firefox | 113+    |
| Gzip DecompressionStream | Safari  | 16.4+   |

> If your browser didn't load the game (shows a full blank screen) try inspecting it and check the message on `<script>` tag, it will say which version your browser needs.

### The flow

1. An HTML file containing the full game is **gzip-compressed** and **base64-encoded**
2. The result is wrapped in a self-extracting HTML loader with a pure-JS inflate implementation (RFC 1951/1952)
3. The browser decompresses the payload at runtime, creates a `Blob` URL, and navigates to it
4. You get a playable DOOM - that you can bookmark, save as a text file. (most applications wouldn't support 4MB of raw text pasted diretcly)


<br>


## Tech Stack

- **Vanilla HTML/CSS/JS** - no frameworks, no build tools for the frontend
- **WebAssembly** - linuxdoom-1.10 compiled with Clang targeting wasm32
- **Python** - encoding pipeline (base64, gzip, data URIs)
- **Pure-JS Inflate** - RFC 1951/1952 decompressor embedded in the loader


## Architecture

```
linuxdoom-1.10 (C source)
    │
    ▼ clang --target=wasm32
    doom.wasm (346 KB)
    │
    ▼ bundle with doom1.wad + JS shim
    doom_single.html (~7 MB)
    │
    ▼ gzip compress + base64 encode
   self-extracting HTML (~4.4 MB rendered)
```

The WASM binary exports all symbols and leaves 49 functions as undefined imports - all provided by a JavaScript shim that implements libc, POSIX I/O, and DOOM's `I_` functions at runtime.


## Encoding Pipeline

The `encoding/` directory contains a Python toolkit that converts HTML files into portable URIs:

- **`html_to_dataurl()`** - straight base64 data URI (works for small files)
- **`html_to_compressed_dataurl()`** - gzip + base64 with an embedded JS decompressor (for large files like DOOM)
- **`html_file_to_base64_dataurl()`** - file-to-file convenience wrapper


## Project Structure

```
.
├-- index.html              # Landing page (loading screen → redirect)
├-- style.css               # Landing page styles
├-- start/                  # Main site with game selector UI
│   ├-- index.html          # "Choose Your Game" hub
│   ├-- doom/               # Full DOOM (single-file HTML + encoded URI)
│   ├-- microdoom_v1.0/     # MicroDOOM v1.0 (HTML + encoded URI)
│   └-- microdoom_v1.1/     # MicroDOOM v1.1
├-- encoding/               # Python encoding & compression pipeline
│   ├-- doomhtml.py         # Bundles WASM + WAD into single HTML
│   ├-- encoding_helpers.py # base64, data URL, gzip utilities
│   └-- encoded_files/      # Timestamped encoded outputs
├-- sources/                # Original unmodified HTML sources
└-- lab/                    # Build experiments & WASM toolchain
    └--- wasm-fizzbuzz/doom/ # C→WASM build pipeline for linuxdoom-1.10
```


<br>


## Run Locally

```bash
# Serve the project (any static server such as Live Server works)
python3 -m http.server 8000

# Open in browser
open http://localhost:8000
```

#### Begin

```bash
cd encoding
python3 -m venv .venv && source .venv/bin/activate  #for mac
pip install requests
```

#### Encoding
```bash
# Encodes the index.html in start/doom/
python encode doom

# Encodes the index.html in start/microdoom_v1.0/
python encode microdoom_v1

# Encodes the index.html in start/microdoom_v1.1/
python encode microdoom_v1.1
```


<br>


## Limitations

- **Browser URI length limits** vary - Chrome caps `data:` URL navigation at ~2 MB
- **Performance** - decompression adds a brief loading delay; WASM DOOM runs perfectly fine on modern browsers
- **Compatibility** - requires a browser with WebAssembly support (all major modern browsers)


<br>


## AI Usage

- **Research**: gzip, base64, how to convert C -> HTML, encoding.
- **microdoom**: I first asked claude to generate new enemies and a new bigger scenario - all my tokens expired before finishind. Then I decided to use ChatGPT - 5 minutes later the enemies where as fast as light and I was spawning INSIDE the obstacles. I had to do the enemies and obstacles by hand.


<br>


## Credits

- **linuxdoom-1.10** - original Linux source release by id Software
- **WASM build pipeline** - based on [diekmann/wasm-fizzbuzz](https://github.com/diekmann/wasm-fizzbuzz)


<br><br>


<hr><br>
<div style="display: flex; justify-content: center; align-items: center; text-align: center; text-justify: center;">
    <sub>&copy; 2026 kmadsdev &middot; Handcrafted by a human</sub>
</div>
<br><hr>
