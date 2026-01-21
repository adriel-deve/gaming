/**
 * Nintendo eShop Price Scraper - 4 Main Regions
 * Fetches prices from BR, US, CA, MX
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Nintendo Price API
const PRICE_API = 'https://api.ec.nintendo.com/v1/price';

// 4 Main regions
const REGIONS = {
    'BR': { currency: 'BRL', name: 'Brasil' },
    'US': { currency: 'USD', name: 'Estados Unidos' },
    'CA': { currency: 'CAD', name: 'Canada' },
    'MX': { currency: 'MXN', name: 'Mexico' },
};

// Exchange rates to BRL (January 2026)
const EXCHANGE_RATES = {
    'BRL': 1.0,
    'USD': 5.80,
    'CAD': 4.20,
    'MXN': 0.32,
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

async function fetchRegionPrices(allNsuids, regionCode, regionInfo) {
    const BATCH_SIZE = 50;
    const prices = {};

    console.log(`\n  [${regionCode}] Fetching prices for ${regionInfo.name}...`);

    for (let i = 0; i < allNsuids.length; i += BATCH_SIZE) {
        const batch = allNsuids.slice(i, i + BATCH_SIZE);
        const batchNum = Math.floor(i / BATCH_SIZE) + 1;
        const totalBatches = Math.ceil(allNsuids.length / BATCH_SIZE);

        if (batchNum % 30 === 0 || batchNum === totalBatches) {
            console.log(`    Batch ${batchNum}/${totalBatches} (${Object.keys(prices).length} prices)`);
        }

        try {
            const result = await fetchPrices(batch, regionCode);

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
                        prices[nsuid] = {
                            msrp,
                            salePrice,
                            discount: msrp > salePrice ? Math.round((1 - salePrice / msrp) * 100) : 0,
                            onSale,
                            currency: regionInfo.currency
                        };
                    }
                }
            }
        } catch (e) {
            // Silent continue
        }

        // Rate limiting
        await new Promise(r => setTimeout(r, 100));
    }

    const salesCount = Object.values(prices).filter(p => p.onSale).length;
    console.log(`  [${regionCode}] OK: ${Object.keys(prices).length} prices, ${salesCount} on sale`);

    return prices;
}

async function main() {
    console.log('='.repeat(70));
    console.log('NINTENDO ESHOP PRICE SCRAPER - 4 REGIONS (BR, US, CA, MX)');
    console.log('='.repeat(70));
    console.log(`Date: ${new Date().toISOString()}`);

    // Load current data
    console.log('\n[1/5] Loading current data...');
    const dataPath = path.join(__dirname, 'multi_region_enriched.json');
    const games = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    console.log(`[OK] ${games.length} games loaded`);

    // Get all NSUIDs
    const allNsuids = games.map(g => g.nsuid).filter(Boolean);
    console.log(`[OK] ${allNsuids.length} NSUIDs to check`);

    // Fetch prices for all 4 regions
    console.log('\n[2/5] Fetching prices from all regions...');

    const allRegionPrices = {};
    for (const [regionCode, regionInfo] of Object.entries(REGIONS)) {
        allRegionPrices[regionCode] = await fetchRegionPrices(allNsuids, regionCode, regionInfo);
    }

    // Summary of fetched prices
    console.log('\n[3/5] Summary of fetched prices:');
    for (const [region, prices] of Object.entries(allRegionPrices)) {
        const count = Object.keys(prices).length;
        const sales = Object.values(prices).filter(p => p.onSale).length;
        console.log(`  ${region}: ${count} prices (${sales} on sale)`);
    }

    // Update games
    console.log('\n[4/5] Updating games with new prices...');
    let gamesUpdated = 0;
    let pricesAdded = 0;

    for (const game of games) {
        const nsuid = game.nsuid;
        if (!nsuid) continue;

        let updated = false;

        // Initialize prices array if needed
        if (!game.prices) game.prices = [];

        // Update each region
        for (const [regionCode, regionPrices] of Object.entries(allRegionPrices)) {
            const priceData = regionPrices[nsuid];
            if (!priceData) continue;

            const regionInfo = REGIONS[regionCode];
            const exchangeRate = EXCHANGE_RATES[regionInfo.currency];

            // Calculate BRL equivalent
            const priceBrl = priceData.salePrice * exchangeRate;
            const msrpBrl = priceData.msrp * exchangeRate;

            // Find existing price for this region
            let existingPrice = game.prices.find(p => p.region === regionCode);

            if (existingPrice) {
                // Update existing
                existingPrice.msrp = priceData.msrp;
                existingPrice.sale_price = priceData.salePrice;
                existingPrice.discount_percent = priceData.discount;
                existingPrice.price_brl = priceBrl;
                existingPrice.msrp_brl = msrpBrl;
                existingPrice.on_sale = priceData.onSale;
                existingPrice.currency = priceData.currency;
                existingPrice.api_updated = true;
            } else {
                // Add new
                game.prices.push({
                    region: regionCode,
                    currency: priceData.currency,
                    msrp: priceData.msrp,
                    sale_price: priceData.salePrice,
                    discount_percent: priceData.discount,
                    price_brl: priceBrl,
                    msrp_brl: msrpBrl,
                    on_sale: priceData.onSale,
                    api_updated: true
                });
                pricesAdded++;
            }

            updated = true;
        }

        if (updated) gamesUpdated++;
    }

    console.log(`[OK] ${gamesUpdated} games updated`);
    console.log(`[OK] ${pricesAdded} new region prices added`);

    // Save
    console.log('\n[5/5] Saving...');
    fs.writeFileSync(dataPath, JSON.stringify(games, null, 2), 'utf8');
    console.log('[OK] Saved to multi_region_enriched.json');

    // Save progress file for tracking
    const progressPath = path.join(__dirname, 'regions_progress.json');
    fs.writeFileSync(progressPath, JSON.stringify({
        date: new Date().toISOString(),
        regions: Object.fromEntries(
            Object.entries(allRegionPrices).map(([r, p]) => [r, Object.keys(p).length])
        ),
        gamesUpdated,
        pricesAdded
    }, null, 2), 'utf8');

    // Final stats
    console.log('\n' + '='.repeat(70));
    console.log('FINAL STATISTICS');
    console.log('='.repeat(70));

    // Count by region
    const regionCounts = { BR: 0, US: 0, CA: 0, MX: 0 };
    const regionSales = { BR: 0, US: 0, CA: 0, MX: 0 };

    for (const game of games) {
        for (const price of (game.prices || [])) {
            if (regionCounts[price.region] !== undefined) {
                regionCounts[price.region]++;
                if (price.on_sale || price.discount_percent > 0) {
                    regionSales[price.region]++;
                }
            }
        }
    }

    console.log('\nPrices by region:');
    for (const region of ['BR', 'US', 'CA', 'MX']) {
        console.log(`  ${region}: ${regionCounts[region]} total, ${regionSales[region]} on sale`);
    }

    // Games with all 4 regions
    let with4Regions = 0;
    let with3Regions = 0;
    let with2Regions = 0;
    let with1Region = 0;

    for (const game of games) {
        const regions = new Set((game.prices || []).map(p => p.region));
        const regionCount = ['BR', 'US', 'CA', 'MX'].filter(r => regions.has(r)).length;

        if (regionCount === 4) with4Regions++;
        else if (regionCount === 3) with3Regions++;
        else if (regionCount === 2) with2Regions++;
        else if (regionCount === 1) with1Region++;
    }

    console.log('\nGames by region coverage:');
    console.log(`  4 regions: ${with4Regions}`);
    console.log(`  3 regions: ${with3Regions}`);
    console.log(`  2 regions: ${with2Regions}`);
    console.log(`  1 region:  ${with1Region}`);

    // Show some Nintendo games
    console.log('\n' + '='.repeat(70));
    console.log('SAMPLE: NINTENDO FIRST-PARTY PRICES');
    console.log('='.repeat(70));

    const nintendoTitles = [
        'Super Mario Odyssey',
        'The Legend of Zelda: Breath of the Wild',
        'Animal Crossing: New Horizons',
        'Mario Kart 8 Deluxe',
        'Pokemon Scarlet',
        'Splatoon 3'
    ];

    for (const game of games) {
        const matchedTitle = nintendoTitles.find(t =>
            game.title.toLowerCase().includes(t.toLowerCase().split(':')[0])
        );

        if (matchedTitle && game.prices && game.prices.length > 0) {
            console.log(`\n${game.title}:`);

            for (const price of game.prices.filter(p => ['BR', 'US', 'CA', 'MX'].includes(p.region))) {
                const saleStr = price.on_sale ? ` (SALE -${price.discount_percent}%)` : '';
                console.log(`  ${price.region}: ${price.currency} ${price.msrp.toFixed(2)} -> ${price.sale_price.toFixed(2)}${saleStr} = R$ ${price.price_brl.toFixed(2)}`);
            }
        }
    }

    console.log('\n' + '='.repeat(70));
    console.log('DONE!');
    console.log('='.repeat(70));
}

main().catch(console.error);
