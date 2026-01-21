/**
 * Nintendo eShop Europe Price Scraper
 *
 * European games have different NSUIDs than American games.
 * This script:
 * 1. Fetches European game list from Nintendo Europe API
 * 2. Maps European NSUIDs to our existing games by title
 * 3. Fetches prices for European countries
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Nintendo Europe Search API
const EU_SEARCH_API = 'http://search.nintendo-europe.com/en/select';

// Nintendo Price API
const PRICE_API = 'https://api.ec.nintendo.com/v1/price';

// European countries
const EU_COUNTRIES = {
    'DE': { currency: 'EUR', name: 'Germany' },
    'FR': { currency: 'EUR', name: 'France' },
    'ES': { currency: 'EUR', name: 'Spain' },
    'IT': { currency: 'EUR', name: 'Italy' },
    'GB': { currency: 'GBP', name: 'United Kingdom' },
    'PT': { currency: 'EUR', name: 'Portugal' },
    'NL': { currency: 'EUR', name: 'Netherlands' },
    'BE': { currency: 'EUR', name: 'Belgium' },
    'AT': { currency: 'EUR', name: 'Austria' },
    'CH': { currency: 'CHF', name: 'Switzerland' },
    'PL': { currency: 'PLN', name: 'Poland' },
    'SE': { currency: 'SEK', name: 'Sweden' },
    'NO': { currency: 'NOK', name: 'Norway' },
    'DK': { currency: 'DKK', name: 'Denmark' },
    'RU': { currency: 'RUB', name: 'Russia' },
    'ZA': { currency: 'ZAR', name: 'South Africa' },
    'AU': { currency: 'AUD', name: 'Australia' },
};

// Exchange rates to BRL
const EXCHANGE_RATES = {
    'EUR': 6.35,
    'GBP': 7.45,
    'CHF': 6.70,
    'PLN': 1.48,
    'SEK': 0.56,
    'NOK': 0.55,
    'DKK': 0.85,
    'RUB': 0.065,
    'ZAR': 0.32,
    'AUD': 3.85,
};

function fetchEuropeanGames(offset = 0, limit = 1000) {
    return new Promise((resolve, reject) => {
        const params = new URLSearchParams({
            'q': '*',
            'fq': 'type:GAME AND system_type:nintendoswitch*',
            'sort': 'sorting_title asc',
            'start': offset.toString(),
            'rows': limit.toString(),
            'wt': 'json'
        });

        const url = `${EU_SEARCH_API}?${params.toString()}`;

        http.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    resolve(result);
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

function fetchPrices(nsuids, country) {
    return new Promise((resolve, reject) => {
        const url = new URL(PRICE_API);
        url.searchParams.set('country', country);
        url.searchParams.set('lang', 'en');
        url.searchParams.set('ids', nsuids.join(','));

        const options = {
            hostname: url.hostname,
            path: url.pathname + url.search,
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', reject);
        req.setTimeout(30000, () => {
            req.destroy();
            reject(new Error('Timeout'));
        });
        req.end();
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
    console.log('NINTENDO ESHOP EUROPE PRICE SCRAPER');
    console.log('='.repeat(70));
    console.log(`Date: ${new Date().toISOString()}`);

    // Load our current games
    console.log('\n[1/5] Loading current games...');
    const dataPath = path.join(__dirname, 'multi_region_enriched.json');
    const games = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log(`[OK] ${games.length} games loaded`);

    // Create title lookup map
    const titleMap = new Map();
    for (const game of games) {
        const normalized = normalizeTitle(game.title);
        titleMap.set(normalized, game);
    }

    // Fetch European games to get their NSUIDs
    console.log('\n[2/5] Fetching European game catalog...');

    let allEuGames = [];
    let offset = 0;
    const LIMIT = 1000;

    while (true) {
        try {
            console.log(`  Fetching offset ${offset}...`);
            const result = await fetchEuropeanGames(offset, LIMIT);

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
            console.log(`  Error at offset ${offset}: ${e.message}`);
            break;
        }

        await new Promise(r => setTimeout(r, 500));
    }

    console.log(`[OK] ${allEuGames.length} European games found`);

    // Map EU NSUIDs to our games
    console.log('\n[3/5] Mapping European NSUIDs to our games...');

    const euNsuidMap = new Map(); // nsuid -> game
    let matched = 0;
    let unmatched = 0;

    for (const euGame of allEuGames) {
        const euNsuid = euGame.nsuid_txt ? euGame.nsuid_txt[0] : null;
        if (!euNsuid) continue;

        const euTitle = euGame.title || '';
        const normalizedEu = normalizeTitle(euTitle);

        // Try exact match
        let ourGame = titleMap.get(normalizedEu);

        // Try fuzzy match if not found
        if (!ourGame) {
            for (const [normTitle, game] of titleMap.entries()) {
                if (normTitle.includes(normalizedEu) || normalizedEu.includes(normTitle)) {
                    ourGame = game;
                    break;
                }
            }
        }

        if (ourGame) {
            euNsuidMap.set(euNsuid, ourGame);
            matched++;
        } else {
            unmatched++;
        }
    }

    console.log(`[OK] Matched ${matched} games, ${unmatched} unmatched`);

    // Get unique EU NSUIDs
    const euNsuids = Array.from(euNsuidMap.keys());
    console.log(`[OK] ${euNsuids.length} EU NSUIDs to check`);

    // Fetch prices for main European countries
    console.log('\n[4/5] Fetching European prices...');

    // Focus on main EU countries
    const mainCountries = ['GB', 'DE', 'FR', 'ES', 'IT', 'PT', 'AU', 'ZA'];

    for (const countryCode of mainCountries) {
        const countryInfo = EU_COUNTRIES[countryCode];
        if (!countryInfo) continue;

        console.log(`\n  [${countryCode}] ${countryInfo.name}...`);

        const BATCH_SIZE = 50;
        let pricesFound = 0;
        let salesFound = 0;

        for (let i = 0; i < euNsuids.length; i += BATCH_SIZE) {
            const batch = euNsuids.slice(i, i + BATCH_SIZE);

            try {
                const result = await fetchPrices(batch, countryCode);

                if (result && result.prices) {
                    for (const priceInfo of result.prices) {
                        const nsuid = String(priceInfo.title_id);
                        const game = euNsuidMap.get(nsuid);
                        if (!game) continue;

                        let msrp = 0;
                        let salePrice = 0;
                        let onSale = false;

                        if (priceInfo.regular_price && priceInfo.regular_price.raw_value) {
                            msrp = parseFloat(String(priceInfo.regular_price.raw_value).replace(',', '.'));
                        }

                        if (priceInfo.discount_price && priceInfo.discount_price.raw_value) {
                            salePrice = parseFloat(String(priceInfo.discount_price.raw_value).replace(',', '.'));
                            onSale = true;
                        } else {
                            salePrice = msrp;
                        }

                        if (msrp > 0) {
                            const exchangeRate = EXCHANGE_RATES[countryInfo.currency] || 1;
                            const priceBrl = salePrice * exchangeRate;
                            const msrpBrl = msrp * exchangeRate;
                            const discount = msrp > salePrice ? Math.round((1 - salePrice / msrp) * 100) : 0;

                            // Add or update price
                            if (!game.prices) game.prices = [];

                            let existing = game.prices.find(p => p.region === countryCode);
                            if (existing) {
                                existing.msrp = msrp;
                                existing.sale_price = salePrice;
                                existing.discount_percent = discount;
                                existing.price_brl = priceBrl;
                                existing.msrp_brl = msrpBrl;
                                existing.on_sale = onSale;
                                existing.currency = countryInfo.currency;
                            } else {
                                game.prices.push({
                                    region: countryCode,
                                    currency: countryInfo.currency,
                                    msrp: msrp,
                                    sale_price: salePrice,
                                    discount_percent: discount,
                                    price_brl: priceBrl,
                                    msrp_brl: msrpBrl,
                                    on_sale: onSale
                                });
                            }

                            pricesFound++;
                            if (onSale) salesFound++;
                        }
                    }
                }
            } catch (e) {
                // Silent continue
            }

            await new Promise(r => setTimeout(r, 100));
        }

        console.log(`    ${pricesFound} prices (${salesFound} on sale)`);
    }

    // Save
    console.log('\n[5/5] Saving...');
    fs.writeFileSync(dataPath, JSON.stringify(games, null, 2), 'utf8');
    console.log('[OK] Saved to multi_region_enriched.json');

    // Stats
    console.log('\n' + '='.repeat(70));
    console.log('SUMMARY');
    console.log('='.repeat(70));

    // Count by region
    const regionCounts = {};
    for (const game of games) {
        for (const price of (game.prices || [])) {
            regionCounts[price.region] = (regionCounts[price.region] || 0) + 1;
        }
    }

    console.log('\nPrices by region:');
    const sortedRegions = Object.entries(regionCounts).sort((a, b) => b[1] - a[1]);
    for (const [region, count] of sortedRegions) {
        console.log(`  ${region}: ${count}`);
    }

    console.log('\n' + '='.repeat(70));
    console.log('DONE!');
    console.log('='.repeat(70));
}

main().catch(console.error);
