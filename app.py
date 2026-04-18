import streamlit as st
import pandas as pd
import io
import os
from procesador import procesar_documento
# Importa aquí tus funciones de supabase_db.py y payphone.py
# from supabase_db import consultar_creditos, restar_creditos
# from payphone import generar_link_pago

st.set_page_config(page_title="FacturaIA Pro - Ecuador", layout="wide")

# --- SIMULACIÓN DE DATOS (Hasta que termines de conectar Supabase) ---
if 'user' not in st.session_state:
    st.session_state.user = {"id": "123", "email": "benito@ejemplo.com"}
if 'creditos' not in st.session_state:
    st.session_state.creditos = 5 # Créditos de cortesía inicial

# --- BARRA LATERAL (Monetización) ---
with st.sidebar:
    st.title("👤 Mi Cuenta")
    st.write(f"**Usuario:** {st.session_state.user['email']}")
    
    # Métrica de créditos con color
    st.metric(label="Créditos Disponibles", value=st.session_state.creditos)
    
    if st.session_state.creditos <= 0:
        st.error("⚠️ Sin créditos. Recarga para continuar.")
    
    st.divider()
    
    st.header("🛒 Planes de Recarga")
    plan = st.radio("Selecciona un plan:", [
        "Plan Básico: 20 facturas ($5)",
        "Plan Contador: 100 facturas ($15)",
        "Plan Estudio: 500 facturas ($50)"
    ])
    
    if st.button("💳 Comprar ahora"):
        # Lógica para extraer el precio según el plan
        precios = {"Plan Básico": 5, "Plan Contador": 15, "Plan Estudio": 50}
        monto = precios[plan.split(":")[0]]
        
        st.write(f"Generando link por ${monto}...")
        # url = generar_link_pago(monto * 100, st.session_state.user['id'])
        # st.link_button("Ir a Pagar con PayPhone", url)
        st.warning("Conecta tu Token de PayPhone en Secrets para activar el botón.")

    st.divider()
    if st.button("Limpiar todo el Lote"):
        st.session_state.historial = []
        st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("🚀 FacturaIA Pro: Extractor Contable Ecuador")

if 'historial' not in st.session_state:
    st.session_state.historial = []

uploaded_files = st.file_uploader("Arrastra tus archivos aquí", type=["pdf", "xml"], accept_multiple_files=True)

# LÓGICA DE PROCESAMIENTO CON BLOQUEO POR CRÉDITOS
if st.button("Procesar Archivos") and uploaded_files:
    if st.session_state.creditos >= len(uploaded_files):
        for uploaded_file in uploaded_files:
            with st.spinner(f"Analizando {uploaded_file.name}..."):
                datos = procesar_documento(uploaded_file.getvalue(), uploaded_file.name)
                if "error" not in datos:
                    st.session_state.historial.append(datos)
                    # Aquí restarías en Supabase realmente:
                    st.session_state.creditos -= 1 
        st.success(f"Procesamiento completado. Te quedan {st.session_state.creditos} créditos.")
    else:
        st.error(f"❌ No tienes suficientes créditos. Intentas procesar {len(uploaded_files)} pero solo tienes {st.session_state.creditos}.")
        st.info("💡 Usa el panel de la izquierda para recargar créditos.")

# ... (El resto de tu código de mostrar resultados y descarga se mantiene igual)

# Mostrar Resultados y Botón de Descarga
if st.session_state.historial:
    df_completo = pd.DataFrame(st.session_state.historial)
    columnas_resumen = [c for c in df_completo.columns if c != 'conceptos']
    
    st.write("### Vista Previa Contable")
    st.dataframe(df_completo[columnas_resumen], use_container_width=True)

    # Generación de Excel Multicapa para Monetización
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Pestaña 1: Resumen General (Cabeceras SRI)
        df_completo[columnas_resumen].to_excel(writer, sheet_name='Resumen_SRI', index=False)
        
        # Pestaña 2: Detalle de Productos (Línea por línea)
        detalles_lista = []
        for factura in st.session_state.historial:
            for item in factura.get("conceptos", []):
                # Cruzamos el item con datos de la factura origen
                item['ruc_emisor'] = factura.get('ruc_emisor')
                item['fecha'] = factura.get('fecha_emision')
                item['nro_factura'] = factura.get('numero_factura')
                detalles_lista.append(item)
        
        pd.DataFrame(detalles_lista).to_excel(writer, sheet_name='Detalle_Productos', index=False)

    st.download_button(
        label="📥 Descargar Reporte Contable Completo (.xlsx)",
        data=output.getvalue(),
        file_name="reporte_contable_ecuador.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )