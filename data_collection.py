import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright, Playwright
import time

YOUTUBE_HOME = "https://www.youtube.com"

def run(p: Playwright):
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(YOUTUBE_HOME)
    
    # Fazer o login
    # procurar o botao de sign in
    # ir pra pagina de sign in
    # preencher login e senha
    # voltar pra home
    # comecar a analise

    time.sleep(5)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)