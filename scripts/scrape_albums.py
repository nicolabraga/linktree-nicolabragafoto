#!/usr/bin/env python3
"""
scrape_albums.py
-----------------
Gera data/albums.json com os álbuns mais recentes do fotógrafo no Fotopix
(https://fotopix.com.br), na mesma estrutura usada pelo site (index.html).

IMPORTANTE — leia antes de usar:
O painel de álbuns do fotógrafo no Fotopix (a lista privada com todos os
álbuns, usada para saber "quais são os 15 mais recentes") fica atrás de
login (Painel do Fotógrafo). Não existe, até onde verificamos, uma página
pública que liste todos os álbuns de um fotógrafo sem autenticação — só é
possível abrir um álbum específico se você já tiver o link dele.

Por isso este script faz login com Playwright usando as credenciais do
Fotopix (definidas como variáveis de ambiente / GitHub Secrets:
FOTOPIX_EMAIL e FOTOPIX_SENHA) e depois lê a lista de álbuns do painel.

Como os seletores exatos do painel autenticado não puderam ser inspecionados
sem fazer login em nome do usuário, a função `extract_albums_from_dashboard`
abaixo está marcada com TODO: depois de rodar `python scripts/scrape_albums.py
--debug` uma vez (o que salva um HTML de depuração em debug_dashboard.html),
ajuste os seletores CSS conforme o HTML real do painel.

Uso:
    pip install playwright
    playwright install chromium
    FOTOPIX_EMAIL=seu@email.com FOTOPIX_SENHA=suasenha python scripts/scrape_albums.py

Saída:
    data/albums.json
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(ROOT, "data", "albums.json")
LOGIN_URL = "https://fotopix.com.br/login"
DASHBOARD_URL = "https://fotopix.com.br/dashboard"
MAX_ALBUMS = 15
FEATURED_COUNT = 5

# Emoji padrão por palavra-chave no título do álbum (mantém o estilo do site)
EMOJI_RULES = [
    ("tarde", "🌆"), ("noite", "🌆"),
    ("beira mar", "🌊"), ("praia", "🌊"),
    ("sabiaguaba", "🚴"), ("ciclismo", "🚴"), ("bike", "🚴"),
    ("track&field", "🏃"), ("corrida", "🏃"), ("run", "🏃"),
    ("evento", "🏆"), ("corporativo", "💼"),
]
DEFAULT_EMOJI = "📷"


def guess_emoji(title: str) -> str:
    t = title.lower()
    for keyword, emoji in EMOJI_RULES:
        if keyword in t:
            return emoji
    return DEFAULT_EMOJI


def extract_albums_from_dashboard(page) -> list:
    """
    TODO: ajustar os seletores abaixo conforme o HTML real do painel do
    fotógrafo (https://fotopix.com.br/dashboard) depois de logado.

    Estrutura esperada de retorno (uma entrada por álbum, já na ordem do
    mais recente para o mais antigo):
        {"id": "23253d", "title": "Beira Mar - Fortaleza",
         "date": "02/07/2026", "url": "https://fotopix.com.br/album/23253d"}
    """
    albums = []

    # Exemplo genérico — troque pelo seletor real de cada card de álbum.
    cards = page.query_selector_all("[data-testid='album-card'], .album-card, li.album-item")

    for card in cards:
        link_el = card.query_selector("a")
        title_el = card.query_selector("[class*=title], h3, h4")
        date_el = card.query_selector("[class*=date], time")

        if not link_el:
            continue

        href = link_el.get_attribute("href") or ""
        if href.startswith("/"):
            href = "https://fotopix.com.br" + href

        album_id = href.rstrip("/").split("/")[-1]
        title = (title_el.inner_text().strip() if title_el else "Álbum")
        date = (date_el.inner_text().strip() if date_el else "")

        albums.append({
            "id": album_id,
            "emoji": guess_emoji(title),
            "title": title,
            "date": date,
            "url": href,
        })

    return albums


def run(debug: bool = False) -> list:
    email = os.environ.get("FOTOPIX_EMAIL")
    senha = os.environ.get("FOTOPIX_SENHA")

    if not email or not senha:
        print(
            "ERRO: defina as variáveis de ambiente FOTOPIX_EMAIL e FOTOPIX_SENHA "
            "(no GitHub, configure como Secrets do repositório).",
            file=sys.stderr,
        )
        sys.exit(1)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(LOGIN_URL, wait_until="networkidle")

        # TODO: ajustar os seletores do formulário de login se necessário.
        page.fill("input[type='email'], input[name='email']", email)
        page.fill("input[type='password'], input[name='password']", senha)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        page.goto(DASHBOARD_URL, wait_until="networkidle")

        if debug:
            debug_path = os.path.join(ROOT, "debug_dashboard.html")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(page.content())
            print(f"HTML de depuração salvo em: {debug_path}")

        albums = extract_albums_from_dashboard(page)
        browser.close()

    return albums[:MAX_ALBUMS]


def save(albums: list) -> None:
    tz = timezone(timedelta(hours=-3))  # America/Fortaleza (BRT)
    payload = {
        "updatedAt": datetime.now(tz).isoformat(),
        "albums": albums,
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"{len(albums)} álbuns salvos em {OUTPUT_PATH}")


if __name__ == "__main__":
    debug_mode = "--debug" in sys.argv
    found_albums = run(debug=debug_mode)

    if not found_albums:
        print(
            "Nenhum álbum encontrado. Rode com --debug e ajuste os seletores em "
            "extract_albums_from_dashboard() usando o debug_dashboard.html gerado.",
            file=sys.stderr,
        )
        sys.exit(1)

    save(found_albums)
