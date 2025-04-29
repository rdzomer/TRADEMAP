import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_trademap(produto, pais, tipo_dado):
    # URL base (ajuste conforme necessário)
    base_url = "https://www.trademap.org/"
    
    try:
        # Configurações de headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Sessão de requests
        session = requests.Session()
        session.headers.update(headers)
        
        # Primeira requisição para obter cookies/sessão
        response = session.get(base_url)
        
        if response.status_code != 200:
            st.error(f"Erro na conexão inicial: Status {response.status_code}")
            return None
        
        # Simulação de busca (este é um exemplo fictício, pode precisar de ajustes)
        search_params = {
            'produto': produto,
            'pais': pais,
            'tipo_dado': tipo_dado
        }
        
        # Exemplo de busca (pode precisar de adaptações)
        search_url = f"{base_url}/search?product={search_params['produto']}&country={search_params['pais']}"
        
        # Realizar a busca
        search_response = session.get(search_url)
        
        if search_response.status_code != 200:
            st.error(f"Erro na busca: Status {search_response.status_code}")
            return None
        
        # Parseamento do HTML
        soup = BeautifulSoup(search_response.text, 'html.parser')
        
        # Exemplo de extração de tabela (precisará ser ajustado)
        tabela = soup.find('table')
        
        if not tabela:
            st.warning("Nenhuma tabela encontrada")
            return None
        
        # Conversão para DataFrame
        df = pd.read_html(str(tabela))[0]
        
        return df
    
    except Exception as e:
        st.error(f"Erro no scraping: {e}")
        return None

# Configuração da página
st.set_page_config(page_title="Consulta TradeMap", layout="centered")
st.title("Consulta ao TradeMap")

# Inputs do usuário
produto = st.text_input("Código ou nome do produto (ex: 1006)")
pais = st.text_input("País ou região (ex: Brazil)")
tipo_dado = st.selectbox("Tipo de dado", ["Trade Indicators", "Yearly", "Quarterly", "Monthly"])

# Botão de busca
buscar = st.button("Buscar Dados")

# Lógica de busca
if buscar:
    if not produto or not pais:
        st.warning("⚠️ Preencha todos os campos obrigatórios antes de buscar os dados.")
    else:
        with st.spinner("Buscando dados..."):
            # Realizar scraping
            df = scrape_trademap(produto, pais, tipo_dado)
            
            # Apresentar resultados
            if df is not None and not df.empty:
                st.success("✅ Dados coletados com sucesso!")
                st.dataframe(df)
                
                # Botão para download
                st.download_button(
                    "📥 Baixar CSV", 
                    df.to_csv(index=False), 
                    file_name="resultado_trademap.csv", 
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Não foi possível encontrar dados para esta consulta.")
