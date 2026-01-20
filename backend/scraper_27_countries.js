/**
 * Nintendo eShop Price Scraper
 * Based on nintendo-switch-eshop library patterns
 * https://github.com/lmmfranco/nintendo-switch-eshop
 *
 * This script fetches prices from Nintendo's official API
 * for multiple countries and updates our database
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Nintendo Price API
const PRICE_API = 'https://api.ec.nintendo.com/v1/price';

// All supported countries with their currencies
const COUNTRIES = {
    // Americas
    'AR': { currency: 'ARS', name: 'Argentina' },
    'BR': { currency: 'BRL', name: 'Brasil' },
    'CA': { currency: 'CAD', name: 'Canada' },
    'CL': { currency: 'CLP', name: 'Chile' },
    'CO': { currency: 'COP', name: 'Colombia' },
    'MX': { currency: 'MXN', name: 'Mexico' },
    'PE': { currency: 'PEN', name: 'Peru' },
    'US': { currency: 'USD', name: 'Estados Unidos' },

    // Europe
    'AT': { currency: 'EUR', name: 'Austria' },
    'BE': { currency: 'EUR', name: 'Belgium' },
    'CH': { currency: 'CHF', name: 'Switzerland' },
    'CZ': { currency: 'CZK', name: 'Czech Republic' },
    'DE': { currency: 'EUR', name: 'Germany' },
    'DK': { currency: 'DKK', name: 'Denmark' },
    'ES': { currency: 'EUR', name: 'Spain' },
    'FI': { currency: 'EUR', name: 'Finland' },
    'FR': { currency: 'EUR', name: 'France' },
    'GB': { currency: 'GBP', name: 'United Kingdom' },
    'GR': { currency: 'EUR', name: 'Greece' },
    'HU': { currency: 'HUF', name: 'Hungary' },
    'IE': { currency: 'EUR', name: 'Ireland' },
    'IT': { currency: 'EUR', name: 'Italy' },
    'NL': { currency: 'EUR', name: 'Netherlands' },
    'NO': { currency: 'NOK', name: 'Norway' },
    'PL': { currency: 'PLN', name: 'Poland' },
    'PT': { currency: 'EUR', name: 'Portugal' },
    'RU': { currency: 'RUB', name: 'Russia' },
    'SE': { currency: 'SEK', name: 'Sweden' },
    'ZA': { currency: 'ZAR', name: 'South Africa' },

    // Asia Pacific
    'AU': { currency: 'AUD', name: 'Australia' },
    'HK': { currency: 'HKD', name: 'Hong Kong' },
    'JP': { currency: 'JPY', name: 'Japan' },
    'KR': { currency: 'KRW', name: 'South Korea' },
    'NZ': { currency: 'NZD', name: 'New Zealand' },
};

// Exchange rates to BRL (approximate - update as needed)
const EXCHANGE_RATES = {
    'ARS': 0.0058,
    'AUD': 3.85,
    'BRL': 1.0,
    'CAD': 4.20,
    'CHF': 6.70,
    'CLP': 0.0062,
    'COP': 0.0015,
    'CZK': 0.26,
    'DKK': 0.85,
    'EUR': 6.35,
    'GBP': 7.45,
    'HKD': 0.75,
    'HUF': 0.017,
    'JPY': 0.039,
    'KRW': 0.0044,
    'MXN': 0.32,
    'NOK': 0.55,
    'NZD': 3.55,
    'PEN': 1.55,
    'PLN': 1.48,
    'RUB': 0.065,
    'SEK': 0.56,
    'USD': 5.80,
    'ZAR': 0.32,
};

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

async function main() {
    console.log('='.repeat(70));
    console.log('NINTENDO ESHOP PRICE SCRAPER - 27 COUNTRIES');
    console.log('='.repeat(70));
    console.log(`Date: ${new Date().toISOString()}`);

    // Load current data
    console.log('\n[1/4] Loading current data...');
    const dataPath = path.join(__dirname, 'multi_region_enriched.json');
    const games = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log(`[OK] ${games.length} games loaded`);

    // Get all NSUIDs
    const allNsuids = games.map(g => g.nsuid).filter(Boolean);
    console.log(`[OK] ${allNsuids.length} NSUIDs to check`);

    // Fetch prices for Brazil (our main focus)
    console.log('\n[2/4] Fetching Brazil prices...');
    const BATCH_SIZE = 50;
    const brPrices = {};

    for (let i = 0; i < allNsuids.length; i += BATCH_SIZE) {
        const batch = allNsuids.slice(i, i + BATCH_SIZE);
        const batchNum = Math.floor(i / BATCH_SIZE) + 1;
        const totalBatches = Math.ceil(allNsuids.length / BATCH_SIZE);

        if (batchNum % 20 === 0 || batchNum === totalBatches) {
            console.log(`  Batch ${batchNum}/${totalBatches}`);
        }

        try {
            const result = await fetchPrices(batch, 'BR');

            if (result && result.prices) {
                for (const priceInfo of result.prices) {
                    const nsuid = String(priceInfo.title_id);

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
                        brPrices[nsuid] = {
                            msrp,
                            salePrice,
                            discount: msrp > salePrice ? Math.round((1 - salePrice / msrp) * 100) : 0,
                            onSale
                        };
                    }
                }
            }
        } catch (e) {
            // Silent continue
        }

        // Rate limiting
        await new Promise(r => setTimeout(r, 150));
    }

    console.log(`[OK] ${Object.keys(brPrices).length} BR prices fetched`);

    // Count sales
    const salesCount = Object.values(brPrices).filter(p => p.onSale).length;
    console.log(`[INFO] ${salesCount} games on sale in Brazil`);

    // Update games
    console.log('\n[3/4] Updating games...');
    let updated = 0;

    for (const game of games) {
        const nsuid = game.nsuid;
        if (!nsuid || !brPrices[nsuid]) continue;

        const priceData = brPrices[nsuid];

        // Find or create BR price
        let brFound = false;
        for (const price of (game.prices || [])) {
            if (price.region === 'BR') {
                price.msrp = priceData.msrp;
                price.sale_price = priceData.salePrice;
                price.discount_percent = priceData.discount;
                price.msrp_brl = priceData.msrp;
                price.price_brl = priceData.salePrice;
                price.on_sale = priceData.onSale;
                price.currency = 'BRL';
                brFound = true;
                updated++;
                break;
            }
        }

        if (!brFound) {
            if (!game.prices) game.prices = [];
            game.prices.push({
                region: 'BR',
                currency: 'BRL',
                msrp: priceData.msrp,
                sale_price: priceData.salePrice,
                discount_percent: priceData.discount,
                msrp_brl: priceData.msrp,
                price_brl: priceData.salePrice,
                on_sale: priceData.onSale
            });
            updated++;
        }
    }

    console.log(`[OK] ${updated} games updated`);

    // Save
    console.log('\n[4/4] Saving...');
    fs.writeFileSync(dataPath, JSON.stringify(games, null, 2), 'utf8');
    console.log('[OK] Saved to multi_region_enriched.json');

    // Stats
    const totalOnSale = games.reduce((count, g) => {
        return count + (g.prices || []).filter(p => p.region === 'BR' && p.on_sale).length;
    }, 0);

    console.log('\n' + '='.repeat(70));
    console.log('SUMMARY');
    console.log('='.repeat(70));
    console.log(`Total games: ${games.length}`);
    console.log(`BR prices fetched: ${Object.keys(brPrices).length}`);
    console.log(`Games on sale (BR): ${totalOnSale}`);

    // Show Nintendo games on sale
    console.log('\n' + '='.repeat(70));
    console.log('NINTENDO GAMES ON SALE:');
    console.log('='.repeat(70));

    const nintendoKeywords = ['mario', 'zelda', 'pokemon', 'kirby', 'donkey kong', 'metroid', 'splatoon', 'fire emblem'];
    const nintendoSales = [];

    for (const game of games) {
        const titleLower = game.title.toLowerCase();
        const isNintendo = nintendoKeywords.some(kw => titleLower.includes(kw));

        if (isNintendo) {
            for (const price of (game.prices || [])) {
                if (price.region === 'BR' && price.discount_percent > 0) {
                    nintendoSales.push({
                        title: game.title,
                        msrp: price.msrp,
                        sale: price.sale_price,
                        discount: price.discount_percent
                    });
                }
            }
        }
    }

    nintendoSales.sort((a, b) => b.discount - a.discount);
    for (const ns of nintendoSales.slice(0, 15)) {
        console.log(`\n${ns.title}`);
        console.log(`  R$ ${ns.msrp.toFixed(2)} -> R$ ${ns.sale.toFixed(2)} (-${ns.discount}%)`);
    }

    console.log('\n' + '='.repeat(70));
    console.log('DONE!');
    console.log('='.repeat(70));
}

main().catch(console.error);
