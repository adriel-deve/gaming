/**
 * Nintendo Switch eShop Scraper
 * Busca TODOS os jogos em promoção usando a biblioteca nintendo-switch-eshop
 */

const { getGamesAmerica } = require('nintendo-switch-eshop');
const fs = require('fs');

// Taxas de conversão para BRL
const CURRENCY_RATES = {
    USD: 5.80,
    CAD: 4.20,
    MXN: 0.32,
    BRL: 1.00,
    EUR: 6.20,
    GBP: 7.20,
    JPY: 0.039,
    AUD: 3.60,
};

/**
 * Buscar jogos em promoção na região US
 */
async function getUSSales() {
    console.log('\n========================================');
    console.log('Buscando jogos nos EUA...');
    console.log('========================================\n');

    try {
        // Buscar todos os jogos da América
        console.log('  Buscando lista completa de jogos...');
        const games = await getGamesAmerica();

        console.log(`  Total de jogos encontrados: ${games.length}`);

        // Filtrar jogos com desconto (que já vêm com informações de preço)
        console.log('  Filtrando jogos em promocao...');
        const gamesWithSales = [];

        for (const game of games) {
            // Verificar se o jogo tem informação de desconto
            if (game.salePrice && game.msrp && game.salePrice < game.msrp) {
                const discount = Math.round((1 - game.salePrice / game.msrp) * 100);

                if (discount > 0) {
                    gamesWithSales.push({
                        title: game.title,
                        nsuid: game.nsuid,
                        store: 'nintendo',
                        platform: 'switch',
                        region: 'US',
                        currency: 'USD',
                        msrp: game.msrp,
                        sale_price: game.salePrice,
                        discount_percent: discount,
                        price_brl: game.salePrice * CURRENCY_RATES.USD,
                        game_id: game.slug || game.nsuid?.replace(/\D/g, ''),
                        url: game.url || `https://www.nintendo.com/us/store/products/${game.slug}`,
                    });
                }
            }

            // Log a cada 500 jogos
            if ((games.indexOf(game) + 1) % 500 === 0) {
                console.log(`    Processados ${games.indexOf(game) + 1}/${games.length} jogos... (${gamesWithSales.length} em promocao)`);
            }
        }

        console.log(`\n[OK] Total de promocoes encontradas: ${gamesWithSales.length}`);
        return gamesWithSales;

    } catch (error) {
        console.error(`[ERRO] Erro ao buscar jogos: ${error.message}`);
        console.error(error);
        return [];
    }
}


/**
 * Main
 */
async function main() {
    console.log('============================================================');
    console.log('NINTENDO SWITCH ESHOP SCRAPER');
    console.log('============================================================');

    // Buscar promoções dos EUA
    const usSales = await getUSSales();

    // Combinar todos os resultados
    const allSales = [...usSales];

    console.log('\n============================================================');
    console.log(`TOTAL GERAL: ${allSales.length} jogos em promocao`);
    console.log('============================================================\n');

    // Mostrar os primeiros 20
    console.log('Primeiros 20 jogos:');
    allSales.slice(0, 20).forEach((game, i) => {
        console.log(`${i + 1}. ${game.title.substring(0, 40).padEnd(40)} -${game.discount_percent}% | $${game.sale_price.toFixed(2)} (R$ ${game.price_brl.toFixed(2)})`);
    });

    if (allSales.length > 20) {
        console.log(`\n... e mais ${allSales.length - 20} jogos`);
    }

    // Salvar em arquivo JSON
    const outputPath = 'nintendo_sales_data.json';
    fs.writeFileSync(outputPath, JSON.stringify(allSales, null, 2));
    console.log(`\nDados salvos em: ${outputPath}`);
}

// Executar
main().catch(error => {
    console.error('Erro fatal:', error);
    process.exit(1);
});
