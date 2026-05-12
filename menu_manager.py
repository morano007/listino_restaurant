import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import io

st.set_page_config(page_title="Listino Prezzi", layout="wide")

# ====================== PASSWORD ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

PASSWORD = "2026"   # ← CAMBIA QUESTA CON LA TUA PASSWORD

def check_login():
    if not st.session_state.logged_in:
        st.title("🔐 Accesso Listino Prezzi")
        pw = st.text_input("Inserisci Password", type="password")
        if st.button("Accedi"):
            if pw == PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Password errata")
        st.stop()

check_login()

# ====================== CONFIG RISTORANTE ======================
if 'ristorante' not in st.session_state:
    st.session_state.ristorante = {
        "nome": "IL TUO RISTORANTE",
        "indirizzo": "Indirizzo completo, Thailandia",
        "telefono": "Tel: +66 XX XXX XXX",
    }

# ====================== CARTELLA IMMAGINI ======================
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
st.sidebar.success("✅ Accesso Effettuato")
if st.sidebar.button("💾 Salva Listino"):
    df.to_csv('listino.csv', index=False)
    st.success("✅ Listino salvato correttamente!")

if st.sidebar.button("🔓 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ====================== INTESTAZIONE ======================
col1, col2 = st.columns([1, 4])
with col1:
    logo_file = st.file_uploader("📸 Carica Logo", type=["png", "jpg", "jpeg"], key="logo_uploader")
    if logo_file:
        logo_path = "images/logo.jpg"
        with open(logo_path, "wb") as f:
            f.write(logo_file.getbuffer())
        st.image(logo_file, width=130)

with col2:
    st.title(st.session_state.ristorante["nome"])
    st.subheader(st.session_state.ristorante["indirizzo"])
    st.subheader(st.session_state.ristorante["telefono"])
    st.caption(f"📅 Listino Prezzi aggiornato al {datetime.now().strftime('%d %B %Y')}")

st.divider()

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📝 Modifica Listino", "➕ Aggiungi Prodotto", "🏷️ Categorie", "📄 Esporta PDF"])

# TAB 1 - Modifica
with tab1:
    st.subheader("Modifica Listino")
    if not df.empty:
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "prezzo": st.column_config.NumberColumn("Prezzo ฿", format="%.0f"),
                "id": st.column_config.NumberColumn(disabled=True),
                "foto": st.column_config.TextColumn(disabled=True)
            }
        )
        if not edited_df.equals(df):
            st.session_state.df = edited_df
    else:
        st.info("Nessun prodotto presente.")

# TAB 2 - Aggiungi
with tab2:
    with st.form("new_product"):
        st.subheader("➕ Nuovo Prodotto")
        col1, col2 = st.columns(2)
        with col1:
            categorie = sorted(df['categoria'].unique().tolist()) if not df.empty else []
            categoria = st.selectbox("Categoria", categorie + ["➕ Nuova Categoria"])
            if categoria == "➕ Nuova Categoria":
                categoria = st.text_input("Nome Nuova Categoria")
            nome = st.text_input("Nome Prodotto")

        with col2:
            prezzo = st.number_input("Prezzo (฿)", min_value=0, step=10, value=100)
            foto = st.file_uploader("Foto Prodotto", type=["jpg", "jpeg", "png"])

        descrizione = st.text_area("Descrizione")
        allergeni = st.text_input("Allergeni (opzionale)")

        if st.form_submit_button("Aggiungi al Listino"):
            if nome and categoria:
                foto_name = ""
                if foto:
                    foto_name = f"{nome.replace(' ', '_')}.jpg"
                    with open(os.path.join("images", foto_name), "wb") as f:
                        f.write(foto.getbuffer())

                new_id = len(df) + 1 if not df.empty else 1
                new_row = pd.DataFrame([{
                    'id': new_id,
                    'categoria': categoria,
                    'nome': nome,
                    'descrizione': descrizione,
                    'prezzo': prezzo,
                    'foto': foto_name,
                    'allergeni': allergeni
                }])
                st.session_state.df = pd.concat([df, new_row], ignore_index=True)
                st.success(f"✅ {nome} aggiunto!")
                st.rerun()

# TAB 3 - Categorie
with tab3:
    st.subheader("Categorie Attuali")
    if not df.empty:
        for cat in sorted(df['categoria'].unique()):
            st.write(f"• {cat}")
    else:
        st.info("Nessuna categoria")

# TAB 4 - PDF
with tab4:
    st.subheader("📄 Esporta Listino PDF")
    if st.button("🚀 Genera PDF Listino", type="primary", use_container_width=True):
        if df.empty:
            st.error("Listino vuoto!")
        else:
            # Generazione PDF semplice tramite HTML
            html = f"""
            <h1 style="text-align:center">{st.session_state.ristorante['nome']}</h1>
            <p style="text-align:center">{st.session_state.ristorante['indirizzo']}<br>
            {st.session_state.ristorante['telefono']}<br>
            Aggiornato: {datetime.now().strftime('%d/%m/%Y')}</p>
            <hr>
            """
            for cat in sorted(df['categoria'].unique()):
                html += f"<h2>{cat}</h2><table style='width:100%'>"
                for _, row in df[df['categoria'] == cat].iterrows():
                    html += f"""
                    <tr>
                        <td><b>{row['nome']}</b><br>{row['descrizione']}</td>
                        <td style="text-align:right"><b>฿ {row['prezzo']:,.0f}</b></td>
                    </tr>
                    """
                html += "</table><br>"

            st.download_button(
                label="📥 Scarica PDF",
                data=html,
                file_name=f"Listino_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )
            st.info("Apri il file HTML e stampa in PDF (Cmd + P → Salva come PDF)")

# Anteprima
st.divider()
st.subheader("Anteprima Listino")
if not df.empty:
    for categoria in sorted(df['categoria'].unique()):
        st.markdown(f"### {categoria}")
        for _, p in df[df['categoria'] == categoria].iterrows():
            cols = st.columns([1, 4, 2])
            with cols[0]:
                if p['foto'] and os.path.exists(os.path.join("images", p['foto'])):
                    st.image(os.path.join("images", p['foto']), width=80)
            with cols[1]:
                st.write(f"**{p['nome']}**")
                if p['descrizione']:
                    st.caption(p['descrizione'])
            with cols[2]:
                st.write(f"**฿ {p['prezzo']:,.0f}**")
            st.divider()