import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

st.set_page_config(page_title="Consulta TradeMap", layout="centered")
st.title("Consulta ao TradeMap via Web Scraping")

produto = st.text_input("Código ou nome do produto (ex: 1006)")
pais = st.text_input("País ou região (ex: Brazil)")
tipo_dado = st.selectbox("Tipo de dado", ["Trade Indicators", "Yearly", "Quarterly", "Monthly"])
buscar = st.button("Buscar Dados")

def configurar_webdriver():
    # Configurações do Chrome
    chrome_options = Options()
    
    # Adicione flags para melhorar compatibilidade
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Tente múltiplos métodos de instalação do ChromeDriver
    try:
        # Método 1: WebDriver Manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e1:
        st.warning(f"Erro no WebDriver Manager: {e1}")
        
        try:
            # Método 2: Caminho padrão do ChromeDriver
            service = Service('/usr/local/bin/chromedriver')  # Caminho padrão no Linux/Mac
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e2:
            st.warning(f"Erro no caminho padrão: {e2}")
            
            try:
                # Método 3: Caminho do ChromeDriver no PATH do sistema
                driver = webdriver.Chrome(options=chrome_options)
                return driver
            except Exception as e3:
                st.error(f"Falha completa na configuração do ChromeDriver: {e3}")
                return None

if buscar:
    if not produto or not pais:
        st.warning("⚠️ Preencha todos os campos obrigatórios antes de buscar os dados.")
    else:
        with st.spinner("Acessando o site TradeMap e coletando os dados..."):
            driver = None
            try:
                # Configurar o WebDriver
                driver = configurar_webdriver()
                
                if driver is None:
                    st.error("Não foi possível iniciar o ChromeDriver. Verifique sua instalação.")
                    st.stop()

                # Resto do código de scraping (mantido igual ao anterior)
                driver.get("https://www.trademap.org/")
                wait = WebDriverWait(driver, 20)

                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Imports']"))).click()
                time.sleep(2)

                campo_produto = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'keyword')]")))
                campo_produto.clear()
                campo_produto.send_keys(produto)
                time.sleep(1)

                campo_pais = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'country')]")))
                campo_pais.clear()
                campo_pais.send_keys(pais)
                time.sleep(2)
                campo_pais.send_keys(Keys.ENTER)
                time.sleep(6)

                tipo_xpath = {
                    "trade indicators": '//button[contains(text(), "Trade Indicators")]',
                    "yearly": '//button[contains(text(), "Yearly Time Series")]',
                    "monthly": '//button[contains(text(), "Monthly Time Series")]',
                    "quarterly": '//button[contains(text(), "Quarterly Time Series")]'
                }.get(tipo_dado.lower())

                if tipo_xpath:
                    wait.until(EC.element_to_be_clickable((By.XPATH, tipo_xpath))).click()
                    time.sleep(5)

                tabelas = pd.read_html(driver.page_source)
                
                if tabelas:
                    df = tabelas[0]
                    st.success("✅ Dados coletados com sucesso!")
                    st.dataframe(df)
                    st.download_button("📥 Baixar CSV", df.to_csv(index=False), file_name="resultado_trademap.csv", mime="text/csv")
                else:
                    st.warning("⚠️ Nenhuma tabela encontrada na página.")

            except Exception as e:
                st.error(f"❌ Erro ao coletar os dados: {e}")
            finally:
                # Garantir que o driver seja fechado
                if driver:
                    driver.quit()
