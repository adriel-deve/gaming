"""
Fetch real game images for games with placeholder images
Uses multiple Nintendo APIs to find actual cover art
"""
import json
import urllib.request
import urllib.parse
import time
import re

def search_nintendo_us(title):
    """Search Nintendo US API"""
    try:
        # Clean title for search
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        search_url = f"https://www.nintendo.com/json/content/get/filter/game?system=switch&limit=5&title={urllib.parse.quote(clean_title[:30])}"

        req = urllib.request.Request(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('games', {}).get('game'):
                games = data['games']['game']
                if not isinstance(games, list):
                    games = [games]
                for game in games:
                    if game.get('front_box_art'):
                        return game['front_box_art']
                    if game.get('image_url'):
                        return game['image_url']
    except:
        pass
    return None

def search_nintendo_eu(title, nsuid=None):
    """Search Nintendo EU API"""
    try:
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        search_url = f"https://searching.nintendo-europe.com/en/select?q={urllib.parse.quote(clean_title[:30])}&fq=type:GAME AND system_names_txt:HAC&rows=5&wt=json"

        req = urllib.request.Request(search_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            for doc in docs:
                if doc.get('image_url'):
                    img = doc['image_url']
                    if not img.startswith('http'):
                        img = 'https:' + img
                    return img
                if doc.get('image_url_sq_s'):
                    img = doc['image_url_sq_s']
                    if not img.startswith('http'):
                        img = 'https:' + img
                    return img
    except:
        pass
    return None

def search_deku_deals(slug):
    """Try to construct image URL from Deku Deals pattern"""
    try:
        # Deku Deals uses predictable image URLs
        img_url = f"https://www.dekudeals.com/images/games/{slug}.jpg"
        req = urllib.request.Request(img_url, method='HEAD', headers={
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                return img_url
    except:
        pass
    return None

print("="*60)
print("FETCHING REAL IMAGES FOR PLACEHOLDER GAMES")
print("="*60)

# Load data
with open('multi_region_enriched.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

print(f"[OK] Loaded {len(games)} games")

# Find games with placeholder images
placeholder_games = [g for g in games if g.get('image', '').startswith('https://api.dicebear.com')]
print(f"[!] Found {len(placeholder_games)} games with placeholder images")

# Try to fetch real images
found = 0
not_found = 0

for i, game in enumerate(placeholder_games):
    title = game.get('title', '')
    slug = game.get('slug', '')
    nsuid = game.get('nsuid', '')

    safe_title = title[:40].encode('ascii', 'replace').decode('ascii')
    print(f"[{i+1}/{len(placeholder_games)}] {safe_title}...", end=' ', flush=True)

    # Try different sources
    image_url = None

    # 1. Try Nintendo EU (usually has more results)
    image_url = search_nintendo_eu(title, nsuid)

    # 2. Try Nintendo US if EU failed
    if not image_url:
        image_url = search_nintendo_us(title)

    if image_url:
        game['image'] = image_url
        found += 1
        print("FOUND!")
    else:
        not_found += 1
        print("not found")

    # Rate limiting
    time.sleep(0.5)

    # Progress update
    if (i + 1) % 25 == 0:
        print(f"\n--- Progress: {i+1}/{len(placeholder_games)} | Found: {found} | Not found: {not_found} ---\n")

print(f"\n[OK] Found real images for {found} games")
print(f"[!] Still using placeholders for {not_found} games")

# Save updated data
with open('multi_region_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False)

print(f"[OK] Saved to multi_region_enriched.json")

print("\n" + "="*60)
print("DONE!")
print("="*60)
