# linktree-nicolabragafoto

Site pessoal de links (estilo Linktree) para @nicolabragafoto — fotógrafo esportivo em Fortaleza, CE.

## Estrutura

```
index.html                       → página principal
style.css                        → estilos (tema escuro com gradientes)
script.js                        → copiar chave Pix, carregar álbuns, auto-atualização
data/albums.json                 → últimos 15 álbuns exibidos na seção "Álbuns recentes"
scripts/scrape_albums.py         → script que regenera data/albums.json a partir do Fotopix
.github/workflows/update-albums.yml → agenda a execução automática do scraper
```

## 1. Subir para o GitHub

Se o repositório `nicolabraga/linktree-nicolabragafoto` ainda não existir, crie um repositório vazio no GitHub com esse nome e depois:

```bash
git init
git add .
git commit -m "Site inicial"
git branch -M main
git remote add origin https://github.com/nicolabraga/linktree-nicolabragafoto.git
git push -u origin main
```

Se o repositório já existir, apenas copie estes arquivos por cima dos existentes e faça commit/push.

## 2. Conectar ao Netlify

1. Em https://app.netlify.com/teams/nicola-emfocosurf , clique em **Add new site → Import an existing project**.
2. Selecione o repositório `nicolabraga/linktree-nicolabragafoto`.
3. Não é necessário build command — é um site estático. Deixe **Publish directory** como raiz (`.`) e **Build command** em branco.
4. Deploy. Toda vez que o GitHub Actions commitar um `data/albums.json` novo (ou você editar qualquer arquivo), o Netlify faz o redeploy automaticamente.

## 3. Atualização automática dos álbuns (GitHub Actions)

O workflow `.github/workflows/update-albums.yml` já está configurado com os horários que você pediu (convertidos de Fortaleza/UTC-3 para UTC, que é o fuso usado pelo GitHub Actions):

- **Seg–Sex:** 07:47, 08:02, 09:02, 18:32, 19:02
- **Sábado:** 08:02, 08:32, 09:02, 18:32, 19:02
- **Domingo:** 08:02, 08:32, 09:02, 09:32, 10:02, 18:32, 19:02

Cada execução roda `scripts/scrape_albums.py`, e se a lista de álbuns mudou, o próprio Action faz commit e push de `data/albums.json` — o que dispara um novo deploy no Netlify automaticamente.

### ⚠️ Passo obrigatório: credenciais do Fotopix

A lista completa de álbuns do fotógrafo fica dentro do **Painel do Fotógrafo**, que exige login — não existe (até onde verificamos) uma página pública que liste todos os seus álbuns sem autenticação. Por isso:

1. Adicione dois *Secrets* no repositório: **Settings → Secrets and variables → Actions → New repository secret**
   - `FOTOPIX_EMAIL` — o e-mail de login no Fotopix
   - `FOTOPIX_SENHA` — a senha de login no Fotopix
2. Rode o workflow manualmente uma vez (**Actions → Atualizar álbuns recentes → Run workflow**) para testar.

O script `scripts/scrape_albums.py` está pronto para logar e navegar até o painel, mas os **seletores CSS usados para ler os cards de álbum são um ponto de partida genérico** — eu não consegui inspecionar o HTML real do painel autenticado (não faço login em contas de terceiros por segurança). Depois de configurar os secrets:

```bash
pip install playwright
playwright install chromium
FOTOPIX_EMAIL=seu@email.com FOTOPIX_SENHA=suasenha python scripts/scrape_albums.py --debug
```

Isso gera `debug_dashboard.html` com o HTML real do painel. Ajuste os seletores dentro da função `extract_albums_from_dashboard()` em `scripts/scrape_albums.py` conforme a estrutura real (classes dos cards, do título e da data de cada álbum).

### Alternativa mais simples

Se preferir não lidar com login automatizado, você mesmo pode editar `data/albums.json` manualmente sempre que quiser atualizar os álbuns — o site lê esse arquivo diretamente, então basta commitar a mudança e o Netlify já republica.

## 4. Atualização em tempo real para quem visita o site

O site já recarrega sozinho a cada 3 minutos no navegador de quem estiver vendo a página (`script.js`), sempre puxando a versão mais recente publicada no Netlify — sem precisar de nenhum processo rodando 24h em servidor.

## Personalização

- **Foto de perfil / cores:** trocar a URL da imagem em `index.html` (`<img class="avatar" ...>`) e as cores do gradiente em `style.css` (`:root`).
- **Links fixos:** editar diretamente os cartões `.link-card` em `index.html`.
- **Nº de álbuns em destaque:** constante `FEATURED_COUNT` em `script.js`.
