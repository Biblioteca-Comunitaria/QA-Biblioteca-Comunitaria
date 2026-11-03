"""Fixtures globais.

Por padrão sobe o `npm run dev` do projeto React automaticamente.
Variáveis de ambiente:
  BASE_URL  -> usa um servidor já rodando (ex.: http://localhost:5173) e não sobe o Vite
  APP_DIR   -> pasta do projeto React (padrão: ../biblioteca-react)
"""
import os
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest

from pages.biblioteca_page import BibliotecaPage

PORTA = 5173


def _aguardar(url: str, tentativas: int = 60):
    for _ in range(tentativas):
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Servidor não respondeu em {url}")


@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("BASE_URL")
    if url:
        yield url.rstrip("/")
        return
    app_dir = Path(os.getenv("APP_DIR", Path(__file__).parent.parent / "biblioteca-react")).resolve()
    if not (app_dir / "package.json").exists():
        pytest.exit(f"Projeto React não encontrado em {app_dir}. Defina APP_DIR ou BASE_URL.")
    if not (app_dir / "node_modules").exists():
        subprocess.run(["npm", "install"], cwd=app_dir, check=True)
    proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", str(PORTA), "--strictPort"],
        cwd=app_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://localhost:{PORTA}"
    try:
        _aguardar(url)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture
def app(page, base_url) -> BibliotecaPage:
    """Página da biblioteca com dados iniciais (cada teste roda em contexto/localStorage novo)."""
    bib = BibliotecaPage(page, base_url)
    bib.abrir("livros")
    return bib
