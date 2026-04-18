import streamlit as st
import pandas as pd
import io
import os
from procesador import procesar_documento

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="FacturaIA Pro", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS para ocultar sidebar y diseñar tarjetas
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main {background-color: #0e1117;}
        .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white;}
        .card {
            border: 1px solid #444;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            background-color: #1e2130;
            transition: transform 0.3s;
        }
        .card:hover {
            transform: scale(1.02);
            border-color: #ff4b4b;
        }
        .price { font-size: 32px; font-weight: bold; margin: 15px 0; }
        .benefit { font-size: 14px; color: #ccc; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO DE SESIÓN ---
if 'creditos' not in st.session_state:
    st.session_state.creditos = 5
if 'historial' not in st.session_state:
    st.session_state.historial = []

# --- 1. BARRA SUPERIOR (HEADER) ---
col_logo, col_space, col_cred, col_acc = st.columns([2, 4, 1.5, 1.5])

with col_logo:
    st.subheader("🚀 FacturaIA Pro")

with col_cred:
    st.metric("Créditos", f"{st.session_state.creditos} disp.")

with col_acc:
    with st.popover("👤 Mi Cuenta"):
        st.write("**Benito Martínez**")
        st.write("benito@ejemplo.com")
        st.divider()
        st.write(f"🔢 Créditos totales: **{st.session_state.creditos}**")
        st.progress(st.session_state.creditos / 100)
        if st.button("Cerrar Sesión"):
            st.info("Saliendo...")

st.divider()

# --- 2. SECCIÓN DE CARGA (CENTRO) ---
st.markdown("<h2 style='text-align: center;'>Extrae datos contables con Inteligencia Artificial</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Sube tus PDFs o XMLs y genera reportes en Excel al instante.</p>", unsafe_allow_html=True)

container_carga = st.container(border=True)
with container_carga:
    uploaded_files = st.file_uploader("", type=["pdf", "xml"], accept_multiple_files=True, label_visibility="collapsed")
    
    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 1, 1])
    with col_btn_2:
        procesar = st.button("✨ Procesar Archivos del SRI")

# Lógica de procesamiento
if procesar and uploaded_files:
    if st.session_state.creditos >= len(uploaded_files):
        for uploaded_file in uploaded_files:
            with st.spinner(f"Leyendo {uploaded_file.name}..."):
                datos = procesar_documento(uploaded_file.getvalue(), uploaded_file.name)
                if "error" not in datos:
                    st.session_state.historial.append(datos)
                    st.session_state.creditos -= 1
        st.success("¡Lote procesado con éxito!")
    else:
        st.error(f"Créditos insuficientes ({st.session_state.creditos}). Necesitas {len(uploaded_files)}.")

# --- 3. RESULTADOS (Si existen) ---
if st.session_state.historial:
    st.write("### 📊 Vista Previa del Reporte")
    df = pd.DataFrame(st.session_state.historial)
    cols = [c for c in df.columns if c != 'conceptos']
    st.dataframe(df[cols], use_container_width=True)
    
    # Aquí iría tu código de generación de Excel (el que ya tienes)
    # ... (omitido por brevedad, pero mantenlo igual)
    st.download_button("📥 Descargar Excel para el SRI", data=b"data", file_name="reporte.xlsx")

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

# --- 4. PLANES DE PRECIOS (TARJETAS) ---
st.markdown("<h3 style='text-align: center;'>Elige el plan ideal para tu flujo</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="card">
            <h4>PERSONA NATURAL</h4>
            <div class="price">$7.00</div>
            <div class="benefit">✅ 25 Facturas / Créditos</div>
            <div class="benefit">✅ Extracción con IA Groq</div>
            <div class="benefit">✅ Exportación Excel básica</div>
            <div class="benefit">❌ Soporte prioritario</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Comprar Básico", key="btn_p1"):
        st.write("Redirigiendo a PayPhone...")

with col2:
    st.markdown("""
        <div class="card" style="border-color: #ff4b4b;">
            <h4 style="color: #ff4b4b;">CONTADOR PRO</h4>
            <div class="price">$20.00</div>
            <div class="benefit">✅ 120 Facturas / Créditos</div>
            <div class="benefit">✅ Procesamiento Masivo</div>
            <div class="benefit">✅ Excel Multicapa Detallado</div>
            <div class="benefit">✅ Soporte vía WhatsApp</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Comprar Pro", key="btn_p2"):
        st.write("Redirigiendo a PayPhone...")

with col3:
    st.markdown("""
        <div class="card">
            <h4>ESTUDIO CONTABLE</h4>
            <div class="price">$60.00</div>
            <div class="benefit">✅ 500 Facturas / Créditos</div>
            <div class="benefit">✅ Los créditos nunca caducan</div>
            <div class="benefit">✅ Análisis de gastos por categoría</div>
            <div class="benefit">✅ Acceso Multi-usuario</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Comprar Estudio", key="btn_p3"):
        st.write("Redirigiendo a PayPhone...")