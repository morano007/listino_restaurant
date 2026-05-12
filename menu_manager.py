import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

st.set_page_config(page_title="Listino Prezzi", layout="wide")
st.title("📋 Listino Prezzi - Ristorante")

# ====================== CREA CARTELLA IMMAGINI ======================
if not os.path.exists("images"):
    os.makedirs("images")

# ====================== CARICAMENTO DATI ======================
if 'df' not in st.session_state:
    if os.path.exists('listino.csv'):
        st.session_state.df = pd.read_csv('listino.csv')
    else:
        st.session_state.df = pd.DataFrame(columns=['id', 'categoria', 'nome', 'descrizione', 'prezzo', 'foto', 'allergeni'])

df = st.session_state.df

# ====================== SIDEBAR ======================
st.sidebar.header("Azioni")
if st.sidebar.button("💾 Salva Listino"):
    df.to_csv('listino.csv', index=False)
    st.success("✅ Listino salvato!")

st.sidebar.info("Valuta: Thai Baht (฿)")

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📝 Modifica Listino", "➕ Aggiungi Prodotto", "🏷️ Categorie", "👀 Anteprima Listino"])

# ------------------- TAB 1: Modifica -------------------
with tab1:
    st.subheader("Modifica Listino Prezzi")
    if not df.empty:
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "prezzo": st.column_config.NumberColumn("Prezzo ฿", format="%.0f"),
                "id": st.column_config.NumberColumn(disabled=True),
                "foto": st.column_config.TextColumn("Nome Foto", disabled=True)
            }
        )
        if not edited_df.equals(df):
            st.session_state.df = edited_df
    else:
        st.info("Nessun prodotto. Aggiungine nella scheda dedicata.")

# ------------------- TAB 2: Aggiungi Prodotto -------------------
with tab2:
    with st.form("new_product"):
        st.subheader("➕ Nuovo Prodotto")
        
        col1, col2 = st.columns(2)
        with col1:
            categorie_esistenti = sorted(df['categoria'].unique().tolist()) if not df.empty else []
            categoria = st.selectbox("Categoria", categorie_esistenti + ["➕ Nuova Categoria"])
            
            if categoria == "➕ Nuova Categoria":
                categoria = st.text_input("Nome nuova categoria")
            
            nome = st.text_input("Nome prodotto")

        with col2:
            prezzo = st.number_input("Prezzo (฿)", min_value=0, step=10, format="%d")
            foto = st.file_uploader("Foto prodotto (opzionale)", type=["jpg", "jpeg", "png"])

        descrizione = st.text_area("Descrizione")
        allergeni = st.text_input("Allergeni (opzionale)")

        if st.form_submit_button("Aggiungi al Listino"):
            if nome and categoria:
                # Salva foto se caricata
                foto_filename = ""
                if foto:
                    foto_filename = f"{nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.jpg"
                    with open(os.path.join("images", foto_filename), "wb") as f:
                        f.write(foto.getbuffer())

                new_id = len(df) + 1 if not df.empty else 1
                new_row = pd.DataFrame([{
                    'id': new_id,
                    'categoria': categoria,
                    'nome': nome,
                    'descrizione': descrizione,
                    'prezzo': prezzo,
                    'foto': foto_filename,
                    'allergeni': allergeni
                }])
                
                st.session_state.df = pd.concat([df, new_row], ignore_index=True)
                st.success(f"✅ {nome} aggiunto!")
                st.rerun()
            else:
                st.error("Nome e Categoria sono obbligatori")

# ------------------- TAB 3: Categorie -------------------
with tab3:
    st.subheader("Gestione Categorie")
    if not df.empty:
        st.write("**Categorie attuali:**")
        for cat in sorted(df['categoria'].unique()):
            st.write(f"• {cat}")
    else:
        st.info("Aggiungi prodotti per vedere le categorie")

# ------------------- TAB 4: Anteprima Listino -------------------
with tab4:
    st.subheader("👀 Anteprima Listino Prezzi")
    if not df.empty:
        df_sorted = df.sort_values(by=['categoria', 'nome'])
        
        for categoria in sorted(df['categoria'].unique()):
            st.markdown(f"### {categoria}")
            prodotti = df_sorted[df_sorted['categoria'] == categoria]
            
            for _, p in prodotti.iterrows():
                cols = st.columns([1, 4, 2])
                
                # Foto
                with cols[0]:
                    if p['foto'] and os.path.exists(os.path.join("images", p['foto'])):
                        try:
                            image = Image.open(os.path.join("images", p['foto']))
                            st.image(image, width=80)
                        except:
                            st.write("📸")
                    else:
                        st.write("📸")
                
                # Nome + Descrizione
                with cols[1]:
                    st.write(f"**{p['nome']}**")
                    if p['descrizione']:
                        st.caption(p['descrizione'])
                
                # Prezzo
                with cols[2]:
                    st.write(f"**฿ {p['prezzo']:,.0f}**")
                
                st.divider()
    else:
        st.info("Listino vuoto")

# Tabella completa
st.divider()
st.subheader("Tabella Completa")
st.dataframe(df.sort_values(by=['categoria', 'nome']), use_container_width=True)