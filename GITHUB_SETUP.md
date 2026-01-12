# 🚀 Como Subir para o GitHub

Siga este guia passo a passo para publicar o **Eshop Pulse** no seu GitHub.

---

## 📋 Pré-requisitos

1. **Conta no GitHub**: [Criar conta](https://github.com/signup) se ainda não tiver
2. **Git instalado**: Verificar com `git --version`
3. **Git configurado com suas credenciais**:
   ```bash
   git config --global user.name "Seu Nome"
   git config --global user.email "seu.email@exemplo.com"
   ```

---

## 🎯 Passo 1: Inicializar Repositório Local

Abra o terminal na pasta do projeto e execute:

```bash
cd "c:\Users\Adrie\.vscode\Site(Projeto)"

# Inicializar Git
git init

# Adicionar todos os arquivos
git add .

# Fazer o commit inicial
git commit -m "feat: Initial commit - Eshop Pulse v1.0

- ✨ Scraper Nintendo eShop multi-região (27 países)
- 🔧 Pipeline de coleta, normalização e armazenamento
- 🌐 API REST com endpoints para ofertas e preços
- 🎨 Frontend com design moderno e responsivo
- 📚 Documentação completa
- 🤖 Scheduler para atualizações automáticas"
```

---

## 🌐 Passo 2: Criar Repositório no GitHub

### Opção A: Via Interface Web (Recomendado)

1. Acesse [github.com/new](https://github.com/new)
2. Configure o repositório:
   - **Nome**: `eshop-pulse` ou `gaming-price-tracker`
   - **Descrição**: `🎮 Comparador global de preços de jogos - Nintendo, PlayStation, Xbox, Steam`
   - **Visibilidade**: Public (para portfólio)
   - ⚠️ **NÃO marque** "Add README" ou "Add .gitignore" (já temos)
3. Clique em **Create repository**
4. Copie a URL do repositório (ex: `https://github.com/seu-usuario/eshop-pulse.git`)

### Opção B: Via GitHub CLI

```bash
# Instale o GitHub CLI se ainda não tiver: https://cli.github.com/

gh repo create eshop-pulse --public --description "🎮 Comparador global de preços de jogos" --source=. --remote=origin
```

---

## 🔗 Passo 3: Conectar e Enviar

```bash
# Adicionar remote (substitua pelo seu usuário)
git remote add origin https://github.com/SEU-USUARIO/eshop-pulse.git

# Verificar remote
git remote -v

# Enviar para o GitHub
git branch -M main
git push -u origin main
```

**Se pedir autenticação:**
- Use seu **Personal Access Token** (não a senha)
- Criar token: Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
- Marque: `repo`, `workflow`

---

## ✅ Passo 4: Verificar

Acesse `https://github.com/SEU-USUARIO/eshop-pulse` e verifique:

- ✅ README.md sendo exibido
- ✅ Todos os arquivos estão lá
- ✅ .gitignore funcionando (data/store/ NÃO deve aparecer)

---

## 🎨 Passo 5: Personalizar (Opcional mas Recomendado)

### A. Adicionar Topics (Tags)

No GitHub, vá em **About** (canto direito) → ⚙️ → Adicione topics:
```
python, gaming, price-tracker, web-scraping, nintendo, playstation,
xbox, steam, api, rest-api, price-comparison, portfolio-project
```

### B. Atualizar README com seus dados

Edite o [README.md](README.md) e substitua:

```markdown
## 👨‍💻 Autor

Desenvolvido por [SEU NOME] como parte do portfólio de projetos gaming.

## 📞 Contato

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Nome](https://linkedin.com/in/seu-perfil)
- Email: seu.email@exemplo.com
```

Depois commit e push:
```bash
git add README.md
git commit -m "docs: Atualizar informações de contato"
git push
```

### C. Adicionar Screenshot (Opcional)

1. Tire um print da interface (index.html aberto)
2. Crie pasta `docs/` e salve como `screenshot.png`
3. Commit:
```bash
mkdir docs
# Copie a imagem para docs/screenshot.png
git add docs/screenshot.png
git commit -m "docs: Adicionar screenshot da aplicação"
git push
```

### D. Configurar GitHub Pages (Para Demo Online)

1. No GitHub: Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: **main** / **(root)**
4. Save
5. Aguarde ~1 minuto
6. Seu site estará em: `https://seu-usuario.github.io/eshop-pulse/`

⚠️ **Nota**: A API não funcionará no GitHub Pages (apenas frontend estático)

---

## 🏷️ Passo 6: Criar Release (Opcional)

Para marcar a versão 1.0:

```bash
# Criar tag
git tag -a v1.0.0 -m "Release v1.0.0 - MVP Completo"

# Enviar tag
git push origin v1.0.0
```

No GitHub: Releases → Draft a new release → escolha a tag `v1.0.0` → Publish

---

## 📝 Commits Futuros

Use mensagens de commit semânticas:

```bash
# Features
git commit -m "feat: Adicionar provider PlayStation Store"

# Fixes
git commit -m "fix: Corrigir bug no parsing de preços JP"

# Docs
git commit -m "docs: Atualizar guia de instalação"

# Style
git commit -m "style: Melhorar responsividade mobile"

# Refactor
git commit -m "refactor: Reorganizar estrutura do pipeline"
```

---

## 🌟 Dicas para Destaque no Portfólio

### 1. Pin no Perfil
No seu perfil GitHub, clique em "Customize your pins" e adicione este repo.

### 2. Adicione Badges
Já incluídos no README.md! Personalize se quiser.

### 3. Escreva um Bom README
Já está pronto! Mas personalize com:
- Seus dados de contato
- Screenshot real
- Link para demo (se hospedar)

### 4. Mantenha Ativo
- Faça commits regulares
- Responda issues
- Aceite contribuições

### 5. Compartilhe
- LinkedIn: Poste sobre o projeto
- Twitter/X: Compartilhe screenshots
- Reddit: r/webdev, r/Python, r/gaming

---

## 🔄 Comandos Git Úteis

```bash
# Ver status
git status

# Ver histórico
git log --oneline

# Criar nova branch para feature
git checkout -b feature/nova-funcionalidade

# Voltar para main
git checkout main

# Atualizar do remoto
git pull origin main

# Ver diferenças
git diff
```

---

## 🐛 Problemas Comuns

### "fatal: not a git repository"
```bash
cd "c:\Users\Adrie\.vscode\Site(Projeto)"
git init
```

### "Permission denied (publickey)"
Use HTTPS ao invés de SSH:
```bash
git remote set-url origin https://github.com/seu-usuario/eshop-pulse.git
```

### "Updates were rejected"
```bash
git pull origin main --rebase
git push origin main
```

### Commits grandes demais
Se tiver arquivos grandes (>50MB), use Git LFS ou adicione ao .gitignore

---

## ✅ Checklist Final

Antes de considerar pronto para o portfólio:

- [ ] README.md completo e personalizado
- [ ] LICENSE incluída
- [ ] .gitignore configurado
- [ ] Código comentado e organizado
- [ ] Documentação clara (ESHOP_SCRAPER.md, SETUP_COMPLETO.md)
- [ ] Screenshot adicionado
- [ ] Topics/tags configuradas
- [ ] Contato atualizado
- [ ] Commit messages claras
- [ ] Repositório público
- [ ] Descrição do repo atrativa

---

## 🎉 Pronto!

Seu projeto está agora no GitHub e pronto para impressionar recrutadores!

**Link para compartilhar:**
```
https://github.com/SEU-USUARIO/eshop-pulse
```

**Próximos passos:**
1. ⭐ Marque como "Featured" no seu perfil
2. 📝 Adicione ao seu currículo/portfólio
3. 🔗 Compartilhe no LinkedIn
4. 🚀 Continue desenvolvendo novas features!

---

**Dúvidas?** Consulte a [documentação do Git](https://git-scm.com/doc) ou [GitHub Docs](https://docs.github.com/)
