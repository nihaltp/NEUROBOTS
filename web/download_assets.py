import urllib.request
import os
import re

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
JS_DIR = os.path.join(STATIC_DIR, 'js')
CSS_DIR = os.path.join(STATIC_DIR, 'css')
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts')

os.makedirs(JS_DIR, exist_ok=True)
os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# 1. Download socket.io
socket_io_url = "https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"
print(f"Downloading {socket_io_url}...")
urllib.request.urlretrieve(socket_io_url, os.path.join(JS_DIR, 'socket.io.js'))

# 1.5 Download nipplejs
nipplejs_url = "https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.10.1/nipplejs.min.js"
print(f"Downloading {nipplejs_url}...")
urllib.request.urlretrieve(nipplejs_url, os.path.join(JS_DIR, 'nipplejs.min.js'))

# 2. Download Google Fonts
font_url = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
print(f"Downloading fonts from {font_url}...")
req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'})
with urllib.request.urlopen(req) as response:
    css_content = response.read().decode('utf-8')

# 3. Find and download all WOFF2 files
urls = re.findall(r'url\((https://[^)]+)\)', css_content)
for url in urls:
    filename = url.split('/')[-1]
    print(f"Downloading font file: {filename}...")
    urllib.request.urlretrieve(url, os.path.join(FONTS_DIR, filename))
    # Replace the URL in CSS
    css_content = css_content.replace(url, f"../fonts/{filename}")

# 4. Save the modified CSS
with open(os.path.join(CSS_DIR, 'fonts.css'), 'w', encoding='utf-8') as f:
    f.write(css_content)

print("Done! All assets downloaded and configured.")
