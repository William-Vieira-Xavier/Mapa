# ---------------------------------------------------------
# 5. PLOTAGEM DAS LTS COM IMAGEM NO POP-UP (TRATADO PARA CELULAR)
# ---------------------------------------------------------
if not df_lts.empty:
    for idx, row in df_lts.iterrows():
        lat = converter_coordenada(row.get('LATITUDE'))
        lon = converter_coordenada(row.get('LONGITUDE'))
        
        if lat is None or lon is None:
            continue
            
        nome = str(row.get('NOME', f'LTS #{idx+1}'))
        coluna = str(row.get('COLUNA', 'Não informada'))
        
        # Tratamento da imagem
        link_img = row.get('LINK IMG')
        img_html = ""
        
        if pd.notna(link_img) and str(link_img).strip():
            url_img = str(link_img).strip()
            
            # Se for um link web (http/https)
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
                img_html = "<br><span style='font-size:11px; color:red;'>⚠️ Link de imagem inválido (deve começar com http/https)</span>"

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
