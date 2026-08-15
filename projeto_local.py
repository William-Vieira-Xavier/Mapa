import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# Configuração da página otimizada para celulares
st.set_page_config(
    page_title="Radar LTS - Renault",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS para ajustar a exibição em telas de celular
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        h1 { font-size: 1.8rem !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Radar de Localização de LTS")

# ---------------------------------------------------------
# 1. CARREGAMENTO E TRATAMENTO DA PLANILHA EXCEL
# ---------------------------------------------------------
EXCEL_PATH = r"C:\Users\pm29058\OneDrive - Renault\PSF Brazil - PSF\Nova pasta\Python\local_LTS\Local_lts_exempl.xlsx"

def converter_coordenada(valor):
    """Converte valores de latitude/longitude para float com segurança."""
    if pd.isna(valor):
        return None
    val_str = str(valor).strip().replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return None

# Garante que a variável df_lts sempre exista
df_lts = pd.DataFrame()

try:
    df_lts = pd.read_excel(EXCEL_PATH)
    # Padroniza nomes das colunas limpando espaços extras
    df_lts.columns = [str(col).strip().upper() for col in df_lts.columns]
    st.caption(f"✓ Planilha sincronizada ({len(df_lts)} registros)")
except Exception as e:
    st.error(f"❌ Erro ao acessar a planilha no OneDrive: {e}")
    st.info("Verifique se o arquivo Excel está fechado e sincronizado no computador.")
    st.stop()

# ---------------------------------------------------------
# 2. OBTENÇÃO DA GEOLOCALIZAÇÃO (GPS DO CELULAR)
# ---------------------------------------------------------
loc = get_geolocation()

user_lat, user_lon = None, None

if loc and isinstance(loc, dict) and 'coords' in loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"📍 GPS Ativo | Lat: {user_lat:.5f}, Lon: {user_lon:.5f}")
else:
    # Se o GPS ainda não carregou, usa a coordenada da 1ª LTS válida
    if not df_lts.empty and 'LATITUDE' in df_lts.columns and 'LONGITUDE' in df_lts.columns:
        df_validos = df_lts.dropna(subset=['LATITUDE', 'LONGITUDE'])
        if not df_validos.empty:
            user_lat = converter_coordenada(df_validos.iloc[0]['LATITUDE'])
            user_lon = converter_coordenada(df_validos.iloc[0]['LONGITUDE'])
    
    # Caso padrão de fallback (Renault - São José dos Pinhais)
    if user_lat is None or user_lon is None:
        user_lat, user_lon = -25.53236, -49.11608

    st.warning("⚠️ Permissão de GPS aguardada... Exibindo posição de referência da fábrica.")

# ---------------------------------------------------------
# 3. CRIAÇÃO DO MAPA / RADAR
# ---------------------------------------------------------
mapa = folium.Map(
    location=[user_lat, user_lon],
    zoom_start=19,
    max_zoom=22,
    tiles="OpenStreetMap"
)

# Posição do Operador (Marcador Vermelho)
folium.Marker(
    location=[user_lat, user_lon],
    popup="<b>Sua Posição (Operador)</b>",
    tooltip="Você está aqui",
    icon=folium.Icon(color="red", icon="user", prefix="fa")
).add_to(mapa)

# Raio do Radar ao redor do operador (50 metros)
folium.Circle(
    location=[user_lat, user_lon],
    radius=50,
    color="#d9534f",
    fill=True,
    fill_color="#d9534f",
    fill_opacity=0.15
).add_to(mapa)

# ---------------------------------------------------------
# 4. INSERÇÃO DAS LTS NO MAPA
# ---------------------------------------------------------
if not df_lts.empty:
    for idx, row in df_lts.iterrows():
        lat = converter_coordenada(row.get('LATITUDE'))
        lon = converter_coordenada(row.get('LONGITUDE'))
        
        if lat is None or lon is None:
            continue
            
        nome = str(row.get('NOME', f'LTS #{idx+1}'))
        coluna = str(row.get('COLUNA', 'Não informada'))
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 150px; font-size: 14px;">
            <h4 style="margin: 0 0 8px 0; color: #1a252f; border-bottom: 2px solid #0275d8; padding-bottom: 4px;">
                {nome}
            </h4>
            <p style="margin: 4px 0;"><b>Coluna:</b> {coluna}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=9,
            color="#0275d8",
            fill=True,
            fill_color="#5bc0de",
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{nome} - Coluna: {coluna}"
        ).add_to(mapa)

# ---------------------------------------------------------
# 5. EXIBIÇÃO NO STREAMLIT
# ---------------------------------------------------------
st_folium(mapa, width="100%", height=550)
