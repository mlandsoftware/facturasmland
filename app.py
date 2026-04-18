import streamlit as st
import pandas as pd
import io
from procesador import procesar_documento

st.set_page_config(page_title="FacturaIA Pro - Ecuador", layout="wide")

# Inicialización de sesión para historial masivo
if 'historial' not in st.session_state:
    st.session_state.historial = []

st.title("🚀 FacturaIA Pro: Extractor Contable Ecuador")
st.markdown("Procesa tus **PDFs** y **XMLs** del SRI de forma masiva y exporta a Excel.")

# Sidebar de control
with st.sidebar:
    st.header("Panel de Control")
    if st.button("Limpiar todo el Lote"):
        st.session_state.historial = []
        st.rerun()
    st.info(f"Facturas en el lote actual: {len(st.session_state.historial)}")

# Carga de archivos
uploaded_files = st.file_uploader("Arrastra tus archivos aquí", type=["pdf", "xml"], accept_multiple_files=True)

if st.button("Procesar Archivos") and uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Analizando {uploaded_file.name}..."):
            datos = procesar_documento(uploaded_file.getvalue(), uploaded_file.name)
            if "error" not in datos:
                st.session_state.historial.append(datos)
    st.success("Procesamiento completado.")

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