import os
import re
import json
import urllib.request
from urllib.error import URLError

# Configuration
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
JS_DIR = os.path.join(STATIC_DIR, 'js')
CSS_DIR = os.path.join(STATIC_DIR, 'css')
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts')
MAP_FILE = os.path.join(os.path.dirname(__file__), 'assets_map.json')

# Ensure directories exist
for directory in [JS_DIR, CSS_DIR, FONTS_DIR]:
    os.makedirs(directory, exist_ok=True)

def download_file(url, save_path):
    print(f"Downloading {url} to {save_path}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read()
            with open(save_path, 'wb') as f:
                f.write(content)
            return content.decode('utf-8', errors='ignore')
    except URLError as e:
        print(f"Failed to download {url}: {e}")
        return None

def process_google_fonts(css_content, css_filename):
    """Parses Google Fonts CSS, downloads WOFF2 files, and returns modified CSS."""
    urls = re.findall(r'url\((https://[^)]+)\)', css_content)
    for url in urls:
        font_filename = url.split('/')[-1]
        font_path = os.path.join(FONTS_DIR, font_filename)
        
        if not os.path.exists(font_path):
            download_file(url, font_path)
            
        # Update URL in CSS to point to local fonts folder
        css_content = css_content.replace(url, f"../fonts/{font_filename}")
        
    css_path = os.path.join(CSS_DIR, css_filename)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return f"css/{css_filename}" # Return relative static path

def localize_html(filepath, asset_map):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find external scripts
    script_urls = re.findall(r'<script\s+[^>]*src=["\'](https?://[^"\']+)["\']', html)
    # Find external stylesheets
    css_urls = re.findall(r'<link\s+[^>]*href=["\'](https?://[^"\']+)["\'][^>]*rel=["\']stylesheet["\']', html)
    # Also find stylesheets where rel is first
    css_urls += re.findall(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\'](https?://[^"\']+)["\']', html)
    
    urls_to_process = list(set(script_urls + css_urls))
    
    for url in urls_to_process:
        if url in asset_map:
            continue
            
        filename = url.split('/')[-1].split('?')[0] # Get filename without query params
        
        if 'fonts.googleapis.com' in url:
            # Handle Google fonts specially
            css_filename = "fonts.css"
            css_content = download_file(url, os.path.join(CSS_DIR, 'google_fonts_temp.css'))
            if css_content:
                local_static_path = process_google_fonts(css_content, css_filename)
                asset_map[url] = local_static_path
                # cleanup temp file
                os.remove(os.path.join(CSS_DIR, 'google_fonts_temp.css'))
        elif url.endswith('.js') or '.js?' in url:
            save_path = os.path.join(JS_DIR, filename)
            if download_file(url, save_path):
                asset_map[url] = f"js/{filename}"
        elif url.endswith('.css') or '.css?' in url:
            save_path = os.path.join(CSS_DIR, filename)
            if download_file(url, save_path):
                asset_map[url] = f"css/{filename}"
                
    # Replace URLs in HTML
    for original_url, local_static_path in asset_map.items():
        if original_url in html:
            # Flask format for static files
            flask_url = f"{{{{ url_for('static', filename='{local_static_path}') }}}}"
            html = html.replace(original_url, flask_url)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {filepath}")

def main():
    asset_map = {}
    
    # Load existing map if it exists
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, 'r', encoding='utf-8') as f:
            asset_map = json.load(f)

    # Process all HTML files in templates directory
    for root, _, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                print(f"Processing {filepath}...")
                localize_html(filepath, asset_map)

    # Save updated map
    with open(MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(asset_map, f, indent=4)
    print(f"Asset map saved to {MAP_FILE}")

if __name__ == "__main__":
    main()
