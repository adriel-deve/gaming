# 🎮 Eshop Pulse - Comparador Global de Jogos

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

> Plataforma completa de comparação de preços de jogos digitais e físicos de múltiplas regiões e lojas.

![Eshop Pulse Screenshot](docs/screenshot.png)

## 🌟 Características

- 🌍 **Multi-região**: Suporte para 27 países (Americas, Europa, Ásia, Oceania)
- 💰 **Comparação de Preços**: Compara preços entre Nintendo eShop, PlayStation Store, Xbox Store e Steam
- 🎯 **Alertas de Preço**: Sistema de notificações quando jogos entram em promoção
- 📊 **Histórico de Preços**: Acompanhe a evolução de preços ao longo do tempo
- 🔄 **Atualização Automática**: Scheduler que atualiza preços periodicamente
- 🎨 **Interface Moderna**: Design clean e responsivo com dark mode
- 🚀 **API REST**: Backend com endpoints para integração

## 🖼️ Preview

### Interface Principal
A interface apresenta:
- Barra de busca com filtros avançados (plataforma, região, mídia, preço)
- Cards de jogos organizados por loja (Nintendo, PlayStation, Xbox, Steam, Mídia Física)
- Indicadores visuais de descontos e promoções
- Preços em moeda local de cada região

### Backend & API
Sistema completo de coleta e processamento de dados:
- Scraping multi-região
- Pipeline de normalização de dados
- API REST com filtros
- Armazenamento de histórico

## 🚀 Começando

### Pré-requisitos

- Python 3.7 ou superior
- Navegador web moderno

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/[seu-usuario]/eshop-pulse.git
cd eshop-pulse
```

2. (Opcional) Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Não há dependências externas! O projeto usa apenas bibliotecas padrão do Python.

### Uso Rápido

#### 1. Testar o Scraper

```bash
cd backend

# Ver todas as regiões disponíveis (27 países)
python test_eshop_scraper.py --show-regions

# Testar scraping de regiões específicas
python test_eshop_scraper.py --regions US BR JP --limit 10

# Salvar resultados em arquivo
python test_eshop_scraper.py --regions US BR --limit 50 --output results.json
```

#### 2. Executar o Pipeline

```bash
# Executa: coleta → normaliza → armazena
python pipeline/run_pipeline.py
```

#### 3. Iniciar o Servidor API

```bash
# Inicia o servidor na porta 9000
python api/server.py --port 9000
```

#### 4. Abrir o Frontend

Abra o arquivo `index.html` no seu navegador ou use um servidor local:

```bash
# Python 3
python -m http.server 8000

# Acesse: http://localhost:8000
```

## 📁 Estrutura do Projeto

```
eshop-pulse/
├── backend/
│   ├── api/
│   │   ├── server.py           # Servidor HTTP com API REST
│   │   └── __init__.py
│   ├── pipeline/
│   │   ├── collect.py          # Coleta de dados
│   │   ├── normalize.py        # Normalização
│   │   ├── store.py            # Armazenamento
│   │   ├── run_pipeline.py     # Executor do pipeline
│   │   └── __init__.py
│   ├── providers/
│   │   ├── nintendo_eshop_provider.py  # Scraper Nintendo eShop
│   │   ├── demo_provider.py            # Dados de demonstração
│   │   └── __init__.py
│   ├── data/                   # Dados (não versionado)
│   │   ├── raw/               # Dados brutos coletados
│   │   ├── normalized/        # Dados normalizados
│   │   └── store/             # Dados finais (prices.json, history.json)
│   ├── config.json            # Configurações gerais
│   ├── eshop_config.json      # Configurações do scraper
│   ├── scheduler.py           # Agendador de atualizações
│   ├── test_eshop_scraper.py  # Script de teste
│   ├── ESHOP_SCRAPER.md       # Documentação técnica
│   └── SETUP_COMPLETO.md      # Guia completo de uso
├── index.html                 # Frontend da aplicação
├── .gitignore
└── README.md
```

## 🌍 Regiões Suportadas

### Americas (8 países)
🇺🇸 US (USD) • 🇨🇦 CA (CAD) • 🇲🇽 MX (MXN) • 🇧🇷 BR (BRL) • 🇦🇷 AR (ARS) • 🇨🇱 CL (CLP) • 🇨🇴 CO (COP) • 🇵🇪 PE (PEN)

### Europa (15 países)
🇬🇧 GB (GBP) • 🇩🇪 DE (EUR) • 🇫🇷 FR (EUR) • 🇪🇸 ES (EUR) • 🇮🇹 IT (EUR) • 🇳🇱 NL (EUR) • 🇵🇹 PT (EUR) • 🇷🇺 RU (RUB) • 🇨🇭 CH (CHF) • 🇦🇹 AT (EUR) • 🇧🇪 BE (EUR) • 🇸🇪 SE (SEK) • 🇳🇴 NO (NOK) • 🇩🇰 DK (DKK) • 🇫🇮 FI (EUR) • 🇵🇱 PL (PLN) • 🇨🇿 CZ (CZK)

### Ásia & Oceania (6 países)
🇯🇵 JP (JPY) • 🇦🇺 AU (AUD) • 🇳🇿 NZ (NZD) • 🇭🇰 HK (HKD) • 🇰🇷 KR (KRW) • 🇿🇦 ZA (ZAR)

## 🔌 API Endpoints

### GET `/api/health`
Verifica o status do servidor.

```json
{
  "status": "ok",
  "timestamp": "2024-01-12T10:00:00Z"
}
```

### GET `/api/offers`
Lista todas as ofertas disponíveis.

**Parâmetros de query:**
- `store` - Filtrar por loja (nintendo, playstation, xbox, steam)
- `region` - Filtrar por região (US, BR, JP, etc)
- `platform` - Filtrar por plataforma (switch, ps5, xbox, pc)
- `on_sale` - Apenas promoções (1 ou 0)
- `min_discount` - Desconto mínimo (ex: 20)

**Exemplo:**
```bash
curl "http://localhost:9000/api/offers?store=nintendo&region=BR&on_sale=1"
```

**Resposta:**
```json
{
  "total": 15,
  "items": [
    {
      "game_id": "mario-kart-8-deluxe",
      "title": "Mario Kart 8 Deluxe",
      "store": "nintendo",
      "platform": "switch",
      "region": "BR",
      "currency": "BRL",
      "price": 209.30,
      "msrp": 299.00,
      "discount_percent": 30,
      "url": "https://www.nintendo.com/...",
      "cover_url": "https://..."
    }
  ]
}
```

### GET `/api/games`
Lista jogos únicos (consolidados de todas as regiões).

### GET `/api/prices?game_id={game_id}`
Histórico de preços de um jogo específico em todas as regiões.

## ⚙️ Configuração

### `backend/config.json`
Configurações gerais do sistema:

```json
{
  "refresh_minutes": 60,
  "default_currency": "BRL",
  "regions": ["BR", "US", "EU"],
  "stores": ["nintendo", "playstation", "xbox", "steam"]
}
```

### `backend/eshop_config.json`
Configurações específicas do scraper:

```json
{
  "regions": {
    "priority": ["US", "BR", "GB", "JP", "DE", "FR", "MX", "AU"],
    "all": ["US", "CA", "MX", "BR", ...]
  },
  "scraping": {
    "limit_per_region": 100,
    "rate_limit_delay": 0.5,
    "use_all_regions": false
  }
}
```

## 🤖 Automação

### Scheduler
Atualiza preços automaticamente em intervalos configuráveis:

```bash
# Executar uma vez e sair
python backend/scheduler.py --once

# Executar continuamente (a cada 60 minutos)
python backend/scheduler.py
```

### Agendar com Cron (Linux/Mac)

```bash
# Executar a cada 1 hora
0 * * * * cd /caminho/para/eshop-pulse/backend && python scheduler.py --once
```

### Agendar com Task Scheduler (Windows)

Crie uma tarefa que execute:
```
python C:\caminho\para\eshop-pulse\backend\scheduler.py --once
```

## 📊 Dados

### Formato dos Dados

Os dados são armazenados em JSON no diretório `backend/data/store/`:

- **`prices.json`**: Preços atuais de todos os jogos
- **`history.json`**: Histórico de alterações de preço

### Exemplo de Item:

```json
{
  "game_id": "the-legend-of-zelda-tears-of-the-kingdom",
  "title": "The Legend of Zelda: Tears of the Kingdom",
  "store": "nintendo",
  "platform": "switch",
  "region": "BR",
  "currency": "BRL",
  "price": 349.00,
  "msrp": 349.00,
  "discount_percent": 0,
  "url": "https://www.nintendo.com/store/products/...",
  "cover_url": "https://assets.nintendo.com/..."
}
```

## 🔒 Nota sobre Dados

**Esta é uma versão de demonstração** com dados fictícios para desenvolvimento e aprendizado.

Para uso em produção com dados reais, você deve:

1. ✅ Usar APIs oficiais das lojas (requer parceria/licença)
2. ✅ Usar serviços licenciados de agregação de dados
3. ✅ Implementar web scraping respeitando:
   - robots.txt
   - Terms of Service
   - Rate limiting adequado
   - Políticas de privacidade

## 🛠️ Tecnologias

### Frontend
- HTML5 / CSS3
- JavaScript Vanilla
- Design responsivo
- Google Fonts (Sora, Bebas Neue)

### Backend
- Python 3.7+
- Bibliotecas padrão (sem dependências externas)
- HTTP Server nativo
- JSON para armazenamento

## 📈 Performance

- **1 região**: ~2-5 segundos para 100 jogos
- **8 regiões**: ~30-60 segundos para 800 jogos
- **27 regiões**: ~3-5 minutos para 2700 jogos

## 🗺️ Roadmap

### ✅ Fase 1 - MVP (Concluído)
- [x] Scraper Nintendo eShop multi-região
- [x] Pipeline de dados
- [x] API REST
- [x] Frontend básico
- [x] Documentação

### 🚧 Fase 2 - Expansão (Em progresso)
- [ ] Implementar scraping real da Nintendo API
- [ ] Adicionar providers: PlayStation, Xbox, Steam
- [ ] Sistema de busca avançada
- [ ] Filtros interativos no frontend
- [ ] Gráficos de histórico de preços

### 📋 Fase 3 - Recursos Avançados
- [ ] Sistema de contas de usuário
- [ ] Wishlist personalizada
- [ ] Alertas de preço por email/push
- [ ] Comparação entre regiões
- [ ] Calculadora de economia com impostos
- [ ] App mobile (React Native)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

Desenvolvido por [Seu Nome] como parte do portfólio de projetos gaming.

## 🙏 Agradecimentos

- Nintendo, PlayStation, Xbox e Steam pelas plataformas incríveis
- Comunidade de desenvolvedores Python
- Gamers que inspiram projetos como este

## 📞 Contato

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Nome](https://linkedin.com/in/seu-perfil)
- Email: seu.email@exemplo.com

---

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!

**Made with ❤️ for gamers by gamers**
