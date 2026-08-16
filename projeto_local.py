import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import os
import time

# Configuração da página para navegação móvel
st.set_page_config(
    page_title="Radar LTS - Renault",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS para otimizar visualização em celulares
st.markdown("""
    <style>
        .block-container { padding-top: 0.8rem; padding-bottom: 0rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        h1 { font-size: 1.6rem !important; text-align: center; margin-bottom: 0px; }
        .stAlert { padding: 8px 12px; margin-bottom: 8px; }
        div.stButton > button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Radar de Localização de LTS")

# Chave dinâmica para forçar atualização real do GPS sem cache
if "gps_key" not in st.session_state:
    st.session_state["gps_key"] = str(time.time())

# ---------------------------------------------------------
# 1. CARREGAMENTO E TRATAMENTO DA PLANILHA EXCEL
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "Local_lts_exempl.xlsx")

def converter_coordenada(valor):
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
    df_lts.columns = [str(col).strip().upper() for col in df_lts.columns]
    st.caption(f"✓ Planilha carregada com sucesso ({len(df_lts)} LTS encontradas)")
except Exception as e:
    st.error(f"❌ Erro ao ler o arquivo 'Local_lts_exempl.xlsx': {e}")
    st.info("💡 Copie o arquivo 'Local_lts_exempl.xlsx' para dentro da MESMA PASTA onde está este arquivo 'principal.py'.")
    st.stop()

# ---------------------------------------------------------
# 2. CAPTURA DE GEOLOCALIZAÇÃO DO CELULAR (GPS ATUALIZÁVEL)
# ---------------------------------------------------------
loc = get_geolocation(component_key=st.session_state["gps_key"])

user_lat, user_lon = None, None

if loc and isinstance(loc, dict) and 'coords' in loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"📍 GPS Ativo | Posição: {user_lat:.5f}, {user_lon:.5f}")
else:
    if not df_lts.empty and 'LATITUDE' in df_lts.columns and 'LONGITUDE' in df_lts.columns:
        df_validos = df_lts.dropna(subset=['LATITUDE', 'LONGITUDE'])
        if not df_validos.empty:
            user_lat = converter_coordenada(df_validos.iloc[0]['LATITUDE'])
            user_lon = converter_coordenada(df_validos.iloc[0]['LONGITUDE'])
    
    if user_lat is None or user_lon is None:
        user_lat, user_lon = -25.53236, -49.11608

    st.warning("⚠️ Permissão de GPS aguardada... Exibindo posição de referência da fábrica.")

# ---------------------------------------------------------
# 3. CONTROLES: BARRA DE BUSCA E BOTÃO DE RECARREGAR
# ---------------------------------------------------------
col_busca, col_btn = st.columns([3, 1])

lts_selecionada = None
foco_lat, foco_lon = user_lat, user_lon
zoom_inicial = 19

with col_busca:
    if not df_lts.empty:
        df_lts['BUSCA_LABEL'] = df_lts.apply(
            lambda r: f"{r.get('NOME', 'Sem Nome')} (Coluna: {r.get('COLUNA', 'N/A')})", axis=1
        )
        opcoes_busca = ["-- Digite ou escolha uma LTS para focar --"] + list(df_lts['BUSCA_LABEL'])
        escolha = st.selectbox("🔍 Buscar LTS:", opcoes_busca, label_visibility="collapsed")
        
        if escolha != "-- Digite ou escolha uma LTS para focar --":
            lts_dados = df_lts[df_lts['BUSCA_LABEL'] == escolha].iloc[0]
            lat_temp = converter_coordenada(lts_dados.get('LATITUDE'))
            lon_temp = converter_coordenada(lts_dados.get('LONGITUDE'))
            
            if lat_temp and lon_temp:
                foco_lat, foco_lon = lat_temp, lon_temp
                zoom_inicial = 21
                lts_selecionada = lts_dados

with col_btn:
    if st.button("🔄 Atualizar"):
        st.session_state["gps_key"] = str(time.time())
        st.rerun()

# ---------------------------------------------------------
# 4. CRIAÇÃO DO MAPA E RADAR (FOLIUM)
# ---------------------------------------------------------
mapa = folium.Map(
    location=[foco_lat, foco_lon],
    zoom_start=zoom_inicial,
    max_zoom=22,
    tiles="OpenStreetMap"
)

# Marcador Vermelho: Posição do Operador
folium.Marker(
    location=[user_lat, user_lon],
    popup="<b>Sua Posição (Operador)</b>",
    tooltip="Você está aqui",
    icon=folium.Icon(color="red", icon="user", prefix="fa")
).add_to(mapa)

# Círculo do radar (15 metros)
folium.Circle(
    location=[user_lat, user_lon],
    radius=15,
    color="#d9534f",
    fill=True,
    fill_color="#d9534f",
    fill_opacity=0.15
).add_to(mapa)

# ---------------------------------------------------------
# 5. PLOTAGEM DAS LTS COM IMAGEM NO POP-UP (OTIMIZADO PARA CELULAR)
# ---------------------------------------------------------
if not df_lts.empty:
    for idx, row in df_lts.iterrows():
        lat = converter_coordenada(row.get('LATITUDE'))
        lon = converter_coordenada(row.get('LONGITUDE'))
        
        if lat is None or lon is None:
            continue
            
        nome = str(row.get('NOME', f'LTS #{idx+1}'))
        coluna = str(row.get('COLUNA', 'Não informada'))
        
        # Tratamento da imagem da coluna "LINK IMG"
        link_img = row.get('LINK IMG')
        img_html = ""
        
        if pd.notna(link_img) and str(link_img).strip():
            url_img = str(link_img).strip()
            
            if url_img.startswith("http"):
                img_html = f"""
                <div style="text-align: center; margin-top: 8px;">
                    <a href="{url_img}" target="_blank">
                        <img src="{url_img}" 
                             alt="Foto da {nome}" 
                             style="width: 100%; max-width: 180px; height: auto; border-radius: 6px; border: 1px solid #ccc;"
                             onerror="this.onerror=null; this.src='https://via.placeholder.com/180x120?text=Erro+ao+carregar+imagem';">
                    </a>
                    <br>
                    <a href="{url_img}" target="_blank" style="font-size: 11px; color: #0275d8; text-decoration: underline;">
                        🔍 Abrir imagem em nova aba
                    </a>
                </div>
                """
            else:
                img_html = "<br><span style='font-size:11px; color:red;'>⚠️ Link precisa iniciar com http/https</span>"

        eh_selecionada = (lts_selecionada is not None) and (row['BUSCA_LABEL'] == lts_selecionada['BUSCA_LABEL'])
        cor_borda = "#28a745" if eh_selecionada else "#0275d8"
        cor_preenchimento = "#5cb85c" if eh_selecionada else "#5bc0de"
        raio_marker = 14 if eh_selecionada else 9
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 180px; max-width: 220px; font-size: 14px; padding: 2px;">
            <h4 style="margin: 0 0 6px 0; color: #1a252f; border-bottom: 2px solid {cor_borda}; padding-bottom: 4px;">
                {nome}
            </h4>
            <p style="margin: 4px 0; color: #333;"><b>Coluna:</b> {coluna}</p>
            {img_html}
        </div>
        """
        
        popup_obj = folium.Popup(popup_html, max_width=250, show=eh_selecionada)
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=raio_marker,
            color=cor_borda,
            fill=True,
            fill_color=cor_preenchimento,
            fill_opacity=0.9,
            popup=popup_obj,
            tooltip=f"{nome} | Coluna: {coluna}"
        ).add_to(mapa)

# ---------------------------------------------------------
# 6. RENDERIZAÇÃO NO STREAMLIT
# ---------------------------------------------------------
st_folium(mapa, width="100%", height=500)
