"""
Fetch real game images from Nintendo store pages
"""
import json
import urllib.request
import urllib.parse
import re
import time

def fetch_image_from_nintendo_store(slug, nsuid):
    """Fetch game image from Nintendo store page"""

    # Clean slug for URL
    clean_slug = slug.replace('-switch', '')

    # Try US store first
    urls_to_try = [
        f'https://www.nintendo.com/us/store/products/{clean_slug}-switch/',
        f'https://www.nintendo.com/us/store/products/{clean_slug}/',
    ]

    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html'
            })
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8')

                # Find game cover image (with NSUID in URL)
                images = re.findall(
                    r'https://assets\.nintendo\.com/image/upload/[^"\']+store/software/switch/' + nsuid + r'/[^"\']+',
                    html
                )
                if images:
                    # Get the best quality image
                    img_url = images[0]
                    # Simplify URL for smaller file
                    img_url = re.sub(r'c_fill,w_\d+', 'c_fill,w_300', img_url)
                    img_url = re.sub(r'dpr_[\d.]+', 'dpr_1.0', img_url)
                    return img_url

                # Try finding any game image
                images = re.findall(
                    r'https://assets\.nintendo\.com/image/upload/[^"\']+store/software/switch/[^"\']+',
                    html
                )
                if images:
                    img_url = images[0]
                    img_url = re.sub(r'c_fill,w_\d+', 'c_fill,w_300', img_url)
                    img_url = re.sub(r'dpr_[\d.]+', 'dpr_1.0', img_url)
                    return img_url

        except urllib.request.HTTPError:
            continue
        except Exception:
            continue

    return None

print("="*60)
print("FETCHING REAL IMAGES FROM NINTENDO STORE")
print("="*60)

# Load data
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] Loaded {len(games)} games")

# Find games with placeholder images
placeholder_games = [g for g in games if g.get('image', '').startswith('https://placehold.co')]
print(f"[!] Found {len(placeholder_games)} games with placeholder images")

# Fetch real images
found = 0
not_found = 0

for i, game in enumerate(placeholder_games):
    title = game.get('title', '')
    slug = game.get('slug', '')
    nsuid = game.get('nsuid', '')

    safe_title = title[:35].encode('ascii', 'replace').decode('ascii')
    print(f"[{i+1}/{len(placeholder_games)}] {safe_title}...", end=' ', flush=True)

    if not nsuid:
        print("no NSUID")
        not_found += 1
        continue

    # Fetch from Nintendo store
    image_url = fetch_image_from_nintendo_store(slug, nsuid)

    if image_url:
        game['image'] = image_url
        found += 1
        print("FOUND!")
    else:
        not_found += 1
        print("not found")

    # Rate limiting
    time.sleep(0.8)

    # Progress update
    if (i + 1) % 20 == 0:
        print(f"\n--- Progress: {i+1}/{len(placeholder_games)} | Found: {found} | Not found: {not_found} ---\n")

print(f"\n{'='*60}")
print(f"[OK] Found real images for {found} games")
print(f"[!] Still missing images for {not_found} games")

# Save updated data
with open('multi_region_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False)

print(f"[OK] Saved to multi_region_enriched.json")
print("="*60)
