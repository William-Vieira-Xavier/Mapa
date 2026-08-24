import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import os
import time

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Radar LTS - Renault",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (FORÇADO TEMA ESCURO)
# ---------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        * { font-family: 'Inter', sans-serif; }

        /* Força fundo escuro geral e texto claro */
        .stApp {
            background-color: #0f172a !important;
            color: #f8fafc !important;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        /* Top Banner Moderno / Minimalista */
        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 16px 20px;
            border-radius: 12px;
            color: #f8fafc;
            text-align: center;
            margin-bottom: 14px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
            position: relative;
            overflow: hidden;
        }
        
        /* Borda decorativa superior */
        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
        }

        .main-header h1 {
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            color: #ffffff !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .main-header .sub-badge {
            display: inline-block;
            margin-top: 6px;
            padding: 3px 10px;
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 20px;
            color: #38bdf8;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        /* Card de Login */
        .login-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 24px;
            max-width: 420px;
            margin: 40px auto;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            text-align: center;
        }
        .login-card h3 {
            color: #f8fafc;
            margin-top: 0;
            margin-bottom: 6px;
            font-weight: 700;
        }
        .login-card p {
            color: #94a3b8;
            font-size: 0.85rem;
            margin-bottom: 20px;
        }

        /* Estilização de Inputs e Selectbox para Modo Escuro */
        div[data-baseweb="select"] > div, input {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border-color: #334155 !important;
        }
        
        div[data-baseweb="popover"] div {
            background-color: #1e293b !important;
            color: #f8fafc !important;
        }

        /* Legenda Estilizada Compacta */
        .legend-box {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .legend-title {
            font-weight: 700;
            font-size: 0.8rem;
            color: #f8fafc;
            text-align: center;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .legend-items {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            gap: 8px;
            font-size: 0.8rem;
            color: #cbd5e1;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
        }
        .dot {
            height: 12px;
            width: 12px;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 6px rgba(0,0,0,0.3);
        }

        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            height: 2.6em;
            font-weight: 600;
            background-color: #0284c7;
            color: white;
            border: none;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            background-color: #0369a1;
            border: none;
            color: white;
        }

        .stSelectbox label { display: none; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# AUTENTICAÇÃO / TELA DE SENHA
# ---------------------------------------------------------
SENHA_CORRETA = "batata"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
        <div class="main-header">
            <h1>RADAR DE LOCALIZAÇÃO LTS</h1>
            <div class="sub-badge">RENAULT &nbsp;|&nbsp; ACESSO RESTRITO</div>
        </div>
    """, unsafe_allow_html=True)

    col_esq, col_centro, col_dir = st.columns([1, 2, 1])
    with col_centro:
        st.markdown("""
            <div class="login-card">
                <h3>Acesso ao Sistema</h3>
                <p>Informe a senha de credencial para continuar</p>
            </div>
        """, unsafe_allow_html=True)
        
        senha_digitada = st.text_input("Senha:", type="password", placeholder="Digite a senha de acesso...", label_visibility="collapsed")
        btn_entrar = st.button("Entrar no Sistema")
        
        if btn_entrar:
            if senha_digitada == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta! Tente novamente.")

    st.stop()

# ---------------------------------------------------------
# CABEÇALHO PRINCIPAL (SISTEMA LIBERADO)
# ---------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <h1>RADAR DE LOCALIZAÇÃO LTS</h1>
        <div class="sub-badge">RENAULT &nbsp;|&nbsp; MONITORAMENTO & NAVEGAÇÃO EM TEMPO REAL</div>
    </div>
""", unsafe_allow_html=True)

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
except Exception as e:
    st.error(f"Erro ao ler o arquivo 'Local_lts_exempl.xlsx': {e}")
    st.info("Copie o arquivo 'Local_lts_exempl.xlsx' para dentro da MESMA PASTA onde está este arquivo 'principal.py'.")
    st.stop()

# ---------------------------------------------------------
# 2. CAPTURA DE GEOLOCALIZAÇÃO DO CELULAR
# ---------------------------------------------------------
loc = get_geolocation(component_key=st.session_state["gps_key"])

user_lat, user_lon = None, None

if loc and isinstance(loc, dict) and 'coords' in loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"GPS Ativo | Posição: `{user_lat:.5f}, {user_lon:.5f}`")
else:
    st.warning("Permissão de GPS aguardada ou indisponível...")

# Define centro padrão do mapa caso não haja GPS nem busca ativa
lat_referencia, lon_referencia = -25.53236, -49.11608
if not df_lts.empty and 'LATITUDE' in df_lts.columns and 'LONGITUDE' in df_lts.columns:
    df_validos = df_lts.dropna(subset=['LATITUDE', 'LONGITUDE'])
    if not df_validos.empty:
        lat_referencia = converter_coordenada(df_validos.iloc[0]['LATITUDE']) or lat_referencia
        lon_referencia = converter_coordenada(df_validos.iloc[0]['LONGITUDE']) or lon_referencia

# ---------------------------------------------------------
# 3. CONTROLES DE BUSCA E NAVEGAÇÃO
# ---------------------------------------------------------
col_busca, col_btn = st.columns([3, 1])

lts_selecionada = None
foco_lat = user_lat if user_lat is not None else lat_referencia
foco_lon = user_lon if user_lon is not None else lon_referencia
zoom_inicial = 19

with col_busca:
    if not df_lts.empty:
        df_lts['BUSCA_LABEL'] = df_lts.apply(
            lambda r: f"{r.get('NOME', 'Sem Nome')} (Tipo: {r.get('TIPO', 'N/A')} - Coluna: {r.get('COLUNA', 'N/A')})", axis=1
        )
        opcoes_busca = ["Digite ou selecione uma LTS para focar..."] + list(df_lts['BUSCA_LABEL'])
        escolha = st.selectbox("Buscar LTS:", opcoes_busca, label_visibility="collapsed")
        
        if escolha != "Digite ou selecione uma LTS para focar...":
            lts_dados = df_lts[df_lts['BUSCA_LABEL'] == escolha].iloc[0]
            lat_temp = converter_coordenada(lts_dados.get('LATITUDE'))
            lon_temp = converter_coordenada(lts_dados.get('LONGITUDE'))
            
            if lat_temp and lon_temp:
                foco_lat, foco_lon = lat_temp, lon_temp
                zoom_inicial = 21
                lts_selecionada = lts_dados

with col_btn:
    if st.button("Atualizar GPS"):
        st.session_state["gps_key"] = str(time.time())
        st.rerun()

# ---------------------------------------------------------
# 4. LEGENDA EXPLICATIVA DAS CORES (ACIMA DO MAPA)
# ---------------------------------------------------------
st.markdown("""
<div class="legend-box">
    <div class="legend-title">Legenda das LTS</div>
    <div class="legend-items">
        <div class="legend-item">
            <span class="dot" style="background-color: #38bdf8; border: 2px solid #0369a1;"></span>
            <span>TÉRREO</span>
        </div>
        <div class="legend-item">
            <span class="dot" style="background-color: #1d4ed8; border: 2px solid #1e3a8a;"></span>
            <span>2°ANDAR</span>
        </div>
        <div class="legend-item">
            <span class="dot" style="background-color: #f59e0b; border: 2px solid #b45309;"></span>
            <span>AÉREO</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CRIAÇÃO DO MAPA E RADAR (FOLIUM)
# ---------------------------------------------------------
mapa = folium.Map(
    location=[foco_lat, foco_lon],
    zoom_start=zoom_inicial,
    max_zoom=22,
    tiles="OpenStreetMap"
)

# SÓ ADICIONA O MARCADOR E O CÍRCULO SE A LOCALIZAÇÃO REAL FOR OBTIDA
if user_lat is not None and user_lon is not None:
    folium.Marker(
        location=[user_lat, user_lon],
        popup="<b>Sua Posição (Operador)</b>",
        tooltip="Você está aqui",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(mapa)

    folium.Circle(
        location=[user_lat, user_lon],
        radius=15,
        color="#ef4444",
        fill=True,
        fill_color="#ef4444",
        fill_opacity=0.15
    ).add_to(mapa)

# ---------------------------------------------------------
# 6. PLOTAGEM DAS LTS
# ---------------------------------------------------------
if not df_lts.empty:
    for idx, row in df_lts.iterrows():
        lat = converter_coordenada(row.get('LATITUDE'))
        lon = converter_coordenada(row.get('LONGITUDE'))
        
        if lat is None or lon is None:
            continue
            
        nome = str(row.get('NOME', f'LTS #{idx+1}'))
        coluna = str(row.get('COLUNA', 'N/I'))
        tipo = str(row.get('TIPO', 'N/A')).strip().upper()
        
        # Cores por TIPO
        if tipo == 'A':
            cor_borda = "#b45309"        # LTS AÉREO
            cor_preenchimento = "#f59e0b"
        elif tipo == 'T2':
            cor_borda = "#1e3a8a"        # LTS 2°ANDAR
            cor_preenchimento = "#1d4ed8"
        else:
            cor_borda = "#0369a1"        # LTS TERREO
            cor_preenchimento = "#38bdf8"

        # Se selecionada na busca, destaca em VERDE
        eh_selecionada = (lts_selecionada is not None) and (row['BUSCA_LABEL'] == lts_selecionada['BUSCA_LABEL'])
        if eh_selecionada:
            cor_borda = "#15803d"
            cor_preenchimento = "#22c55e"
            
        raio_marker = 14 if eh_selecionada else 9
        
        # Popup Imagem
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
                             style="width: 100%; max-width: 180px; height: auto; border-radius: 8px; border: 1px solid #cbd5e1;"
                             onerror="this.onerror=null; this.src='https://via.placeholder.com/180x120?text=Sem+Imagem';">
                    </a>
                    <br>
                    <a href="{url_img}" target="_blank" style="font-size: 11px; color: #0284c7; text-decoration: none; font-weight: bold;">
                        Expandir foto
                    </a>
                </div>
                """

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 180px; max-width: 220px; padding: 2px;">
            <h4 style="margin: 0 0 6px 0; color: #0f172a; border-bottom: 2px solid {cor_borda}; padding-bottom: 4px;">
                {nome}
            </h4>
            <p style="margin: 4px 0; color: #334155; font-size: 13px;"><b>Tipo:</b> {tipo}</p>
            <p style="margin: 4px 0; color: #334155; font-size: 13px;"><b>Coluna:</b> {coluna}</p>
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
            tooltip=f"{nome} | Tipo: {tipo} | Col: {coluna}"
        ).add_to(mapa)

# ---------------------------------------------------------
# 7. RENDERIZAÇÃO DO MAPA (ALTURA 350px)
# ---------------------------------------------------------
st_folium(mapa, width="100%", height=350)
