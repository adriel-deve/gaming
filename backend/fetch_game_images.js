/**
 * Fetch game cover images from Nintendo API
 * Uses the Nintendo of America games API to get box art URLs
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Nintendo of America Games API
const NOA_API = 'https://www.nintendo.com/json/content/get/filter/game';

// Alternative: Nintendo Europe API (has images)
const NOE_SEARCH = 'http://search.nintendo-europe.com/en/select';

async function fetchEuropeGames(offset = 0, limit = 200) {
    return new Promise((resolve, reject) => {
        const params = new URLSearchParams({
            'q': '*',
            'fq': 'type:GAME AND system_type:nintendoswitch*',
            'sort': 'sorting_title asc',
            'start': offset.toString(),
            'rows': limit.toString(),
            'wt': 'json',
            'fl': 'title,nsuid_txt,image_url,image_url_sq_s,url'
        });

        const url = `${NOE_SEARCH}?${params.toString()}`;

        require('http').get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

function normalizeTitle(title) {
    return title
        .toLowerCase()
        .replace(/[™®©]/g, '')
        .replace(/\s+/g, ' ')
        .replace(/['']/g, "'")
        .replace(/[:–—-]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

async function main() {
    console.log('='.repeat(70));
    console.log('FETCHING GAME COVER IMAGES FROM NINTENDO EUROPE API');
    console.log('='.repeat(70));

    // Load our games
    console.log('\n[1/4] Loading games...');
    const dataPath = path.join(__dirname, 'multi_region_enriched.json');
    const games = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log(`[OK] ${games.length} games loaded`);

    // Create title lookup map
    const titleMap = new Map();
    for (const game of games) {
        const normalized = normalizeTitle(game.title);
        titleMap.set(normalized, game);
    }

    // Fetch European games with images
    console.log('\n[2/4] Fetching European game catalog with images...');

    let allEuGames = [];
    let offset = 0;
    const LIMIT = 1000;

    while (true) {
        try {
            console.log(`  Fetching offset ${offset}...`);
            const result = await fetchEuropeGames(offset, LIMIT);

            if (result.response && result.response.docs) {
                const docs = result.response.docs;
                allEuGames.push(...docs);
                console.log(`    Got ${docs.length} games (total: ${allEuGames.length})`);

                if (docs.length < LIMIT) {
                    break;
                }
                offset += LIMIT;
            } else {
                break;
            }
        } catch (e) {
            console.log(`  Error: ${e.message}`);
            break;
        }

        await new Promise(r => setTimeout(r, 300));
    }

    console.log(`[OK] ${allEuGames.length} European games fetched`);

    // Map images to our games
    console.log('\n[3/4] Mapping images to games...');

    let matched = 0;
    let withImages = 0;

    for (const euGame of allEuGames) {
        const euTitle = euGame.title || '';
        const normalizedEu = normalizeTitle(euTitle);

        // Try to find our game
        let ourGame = titleMap.get(normalizedEu);

        // Try partial match
        if (!ourGame) {
            for (const [normTitle, game] of titleMap.entries()) {
                if (normTitle.includes(normalizedEu) || normalizedEu.includes(normTitle)) {
                    ourGame = game;
                    break;
                }
            }
        }

        if (ourGame) {
            matched++;

            // Get image URL
            let imageUrl = euGame.image_url_sq_s || euGame.image_url;
            if (imageUrl) {
                // Ensure HTTPS
                if (imageUrl.startsWith('//')) {
                    imageUrl = 'https:' + imageUrl;
                } else if (imageUrl.startsWith('http://')) {
                    imageUrl = imageUrl.replace('http://', 'https://');
                }

                ourGame.image = imageUrl;
                withImages++;
            }
        }
    }

    console.log(`[OK] Matched ${matched} games`);
    console.log(`[OK] ${withImages} games with images`);

    // Save
    console.log('\n[4/4] Saving...');
    fs.writeFileSync(dataPath, JSON.stringify(games, null, 2), 'utf8');
    console.log('[OK] Saved to multi_region_enriched.json');

    // Stats
    const gamesWithImages = games.filter(g => g.image).length;
    console.log(`\n[INFO] Total games with images: ${gamesWithImages}/${games.length}`);

    // Show examples
    console.log('\n' + '='.repeat(70));
    console.log('EXAMPLES:');
    console.log('='.repeat(70));

    let shown = 0;
    for (const game of games) {
        if (game.image && game.title.toLowerCase().includes('mario')) {
            console.log(`\n${game.title}`);
            console.log(`  Image: ${game.image.substring(0, 80)}...`);
            shown++;
            if (shown >= 5) break;
        }
    }

    console.log('\n' + '='.repeat(70));
    console.log('DONE!');
    console.log('='.repeat(70));
}

main().catch(console.error);
