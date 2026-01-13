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
 * Buscar TODOS os jogos da região US (com e sem promoção)
 */
async function getUSGames() {
    console.log('\n========================================');
    console.log('Buscando TODOS os jogos nos EUA...');
    console.log('========================================\n');

    try {
        // Buscar todos os jogos da América
        console.log('  Buscando lista completa de jogos...');
        const games = await getGamesAmerica();

        console.log(`  Total de jogos encontrados: ${games.length}`);

        // Processar TODOS os jogos (com e sem desconto)
        console.log('  Processando todos os jogos...');
        const allGames = [];
        let gamesWithSales = 0;

        for (const game of games) {
            // Verificar se o jogo tem informação de preço
            if (game.msrp && game.msrp > 0) {
                // Determinar se tem desconto
                const salePrice = game.salePrice || game.msrp;
                const hasDiscount = game.salePrice && game.salePrice < game.msrp;
                const discount = hasDiscount ? Math.round((1 - game.salePrice / game.msrp) * 100) : 0;

                if (hasDiscount) {
                    gamesWithSales++;
                }

                allGames.push({
                    title: game.title,
                    nsuid: game.nsuid,
                    store: 'nintendo',
                    platform: 'switch',
                    region: 'US',
                    currency: 'USD',
                    msrp: game.msrp,
                    sale_price: salePrice,
                    discount_percent: discount,
                    msrp_brl: game.msrp * CURRENCY_RATES.USD,
                    price_brl: salePrice * CURRENCY_RATES.USD,
                    game_id: game.slug || game.nsuid?.replace(/\D/g, ''),
                    url: game.url || `https://www.nintendo.com/us/store/products/${game.slug}`,
                });
            }

            // Log a cada 500 jogos
            if ((games.indexOf(game) + 1) % 500 === 0) {
                console.log(`    Processados ${games.indexOf(game) + 1}/${games.length} jogos... (${allGames.length} com preco, ${gamesWithSales} em promocao)`);
            }
        }

        console.log(`\n[OK] Total de jogos com preco: ${allGames.length}`);
        console.log(`[OK] Jogos em promocao: ${gamesWithSales}`);
        console.log(`[OK] Jogos sem promocao: ${allGames.length - gamesWithSales}`);
        return allGames;

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
    console.log('NINTENDO SWITCH ESHOP SCRAPER - CATALOGO COMPLETO');
    console.log('============================================================');

    // Buscar TODOS os jogos dos EUA
    const usGames = await getUSGames();

    // Combinar todos os resultados
    const allGames = [...usGames];

    console.log('\n============================================================');
    console.log(`TOTAL GERAL: ${allGames.length} jogos no catalogo`);
    console.log('============================================================\n');

    // Mostrar os primeiros 20
    console.log('Primeiros 20 jogos:');
    allGames.slice(0, 20).forEach((game, i) => {
        const priceInfo = game.discount_percent > 0
            ? `-${game.discount_percent}% | $${game.sale_price.toFixed(2)} (era $${game.msrp.toFixed(2)})`
            : `$${game.msrp.toFixed(2)}`;
        console.log(`${i + 1}. ${game.title.substring(0, 40).padEnd(40)} ${priceInfo}`);
    });

    if (allGames.length > 20) {
        console.log(`\n... e mais ${allGames.length - 20} jogos`);
    }

    // Salvar em arquivo JSON
    const outputPath = 'nintendo_sales_data.json';
    fs.writeFileSync(outputPath, JSON.stringify(allGames, null, 2));
    console.log(`\nDados salvos em: ${outputPath}`);
}

// Executar
main().catch(error => {
    console.error('Erro fatal:', error);
    process.exit(1);
});
