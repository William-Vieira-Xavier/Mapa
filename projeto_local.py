import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import os

# Configuração da página para navegação móvel
st.set_page_config(
    page_title="Radar LTS - Renault",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS para ajustar a exibição em telas de celular
st.markdown("""
    <style>
        .block-container { padding-top: 0.8rem; padding-bottom: 0rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        h1 { font-size: 1.6rem !important; text-align: center; margin-bottom: 0px; }
        .stAlert { padding: 8px 12px; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Radar de Localização de LTS")

# ---------------------------------------------------------
# 1. CARREGAMENTO E TRATAMENTO DA PLANILHA EXCEL
# ---------------------------------------------------------
# Pega automaticamente o caminho da pasta atual onde está o principal.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "Local_lts_exempl.xlsx")

def converter_coordenada(valor):
    """Converte valores de latitude/longitude (texto ou número) para float com segurança."""
    if pd.isna(valor):
        return None
    val_str = str(valor).strip().replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return None

df_lts = pd.DataFrame()

try:
    df_lts = pd.read_excel(EXCEL_PATH)
    # Limpa espaços em branco e converte nomes das colunas para maiúsculas
    df_lts.columns = [str(col).strip().upper() for col in df_lts.columns]
    st.caption(f"✓ Planilha carregada com sucesso ({len(df_lts)} LTS encontradas)")
except Exception as e:
    st.error(f"❌ Erro ao ler o arquivo 'Local_lts_exempl.xlsx': {e}")
    st.info("💡 Copie o arquivo 'Local_lts_exempl.xlsx' para dentro da MESMA PASTA onde está este arquivo 'principal.py'.")
    st.stop()

# ---------------------------------------------------------
# 2. CAPTURA DE GEOLOCALIZAÇÃO DO CELULAR (GPS)
# ---------------------------------------------------------
loc = get_geolocation()

user_lat, user_lon = None, None

if loc and isinstance(loc, dict) and 'coords' in loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"📍 GPS Ativo | Posição: {user_lat:.5f}, {user_lon:.5f}")
else:
    # Se o GPS ainda não retornou localização, usa a 1ª LTS válida como posição inicial do mapa
    if not df_lts.empty and 'LATITUDE' in df_lts.columns and 'LONGITUDE' in df_lts.columns:
        df_validos = df_lts.dropna(subset=['LATITUDE', 'LONGITUDE'])
        if not df_validos.empty:
            user_lat = converter_coordenada(df_validos.iloc[0]['LATITUDE'])
            user_lon = converter_coordenada(df_validos.iloc[0]['LONGITUDE'])
    
    # Fallback padrão (Renault São José dos Pinhais) caso não haja coordenadas válidas
    if user_lat is None or user_lon is None:
        user_lat, user_lon = -25.53236, -49.11608

    st.warning("⚠️ Permissão de GPS aguardada... Exibindo posição de referência da fábrica.")

# ---------------------------------------------------------
# 3. CRIAÇÃO DO MAPA E RADAR (FOLIUM)
# ---------------------------------------------------------
mapa = folium.Map(
    location=[user_lat, user_lon],
    zoom_start=19,
    max_zoom=22,
    tiles="OpenStreetMap"
)

# Marcador Vermelho: Posição do Operador/Celular
folium.Marker(
    location=[user_lat, user_lon],
    popup="<b>Sua Posição (Operador)</b>",
    tooltip="Você está aqui",
    icon=folium.Icon(color="red", icon="user", prefix="fa")
).add_to(mapa)

# Raio translúcido simulando a área do radar (50 metros)
folium.Circle(
    location=[user_lat, user_lon],
    radius=50,
    color="#d9534f",
    fill=True,
    fill_color="#d9534f",
    fill_opacity=0.12
).add_to(mapa)

# ---------------------------------------------------------
# 4. PLOTAGEM DAS LTS DA PLANILHA NO MAPA
# ---------------------------------------------------------
if not df_lts.empty:
    for idx, row in df_lts.iterrows():
        lat = converter_coordenada(row.get('LATITUDE'))
        lon = converter_coordenada(row.get('LONGITUDE'))
        
        # Pula com segurança se a linha não tiver coordenadas
        if lat is None or lon is None:
            continue
            
        nome = str(row.get('NOME', f'LTS #{idx+1}'))
        coluna = str(row.get('COLUNA', 'Não informada'))
        
        # Pop-up estilizado com Nome e Coluna
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 160px; font-size: 14px; padding: 2px;">
            <h4 style="margin: 0 0 6px 0; color: #1a252f; border-bottom: 2px solid #0275d8; padding-bottom: 4px;">
                {nome}
            </h4>
            <p style="margin: 4px 0; color: #333;"><b>Coluna:</b> {coluna}</p>
        </div>
        """
        
        # Bolinha/Marcador da LTS
        folium.CircleMarker(
            location=[lat, lon],
            radius=9,
            color="#0275d8",
            fill=True,
            fill_color="#5bc0de",
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{nome} | Coluna: {coluna}"
        ).add_to(mapa)

# ---------------------------------------------------------
# 5. RENDERIZAÇÃO NO STREAMLIT
# ---------------------------------------------------------
st_folium(mapa, width="100%", height=550)
