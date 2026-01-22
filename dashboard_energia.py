import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
from io import BytesIO
import tempfile
import subprocess

# ================================
# CONFIGURACIÓN DE LA PÁGINA
# ================================
st.set_page_config(
    page_title="Coberturas de Inventario - Gerencia de Energía",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================
# ESTILOS CSS PROFESIONALES
# ================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    .main {
        background: #F5F7FA;
    }
    
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 100% !important;
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #00A3E0 0%, #0077B6 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,163,224,0.2);
    }
    
    .header-container h1 {
        color: white;
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
    }
    
    .header-container p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E8EBED;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        height: 100%;
    }
    
    .kpi-card:hover {
        box-shadow: 0 4px 16px rgba(0,163,224,0.15);
        border-color: #00A3E0;
    }
    
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #7F8C8D;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #2C3E50;
        line-height: 1.2;
    }
    
    .kpi-delta {
        font-size: 0.85rem;
        color: #7F8C8D;
        margin-top: 0.5rem;
    }
    
    /* Sections */
    .section-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E8EBED;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 1rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: white;
        border-bottom: 2px solid #E8EBED;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #7F8C8D;
        font-weight: 500;
        padding: 1rem 1.5rem;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #00A3E0;
        background: rgba(0,163,224,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        color: #00A3E0 !important;
        border-bottom-color: #00A3E0 !important;
        font-weight: 600 !important;
    }
    
    /* Dataframes */
    .dataframe {
        font-size: 0.85rem !important;
        border: 1px solid #E8EBED !important;
    }
    
    .dataframe thead th {
        background: #F8FAFB !important;
        color: #2C3E50 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        padding: 0.75rem !important;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(0,163,224,0.05) !important;
    }
    
    /* Botones */
    .stButton>button {
        background: linear-gradient(135deg, #00A3E0, #0077B6);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,163,224,0.25);
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 16px rgba(0,163,224,0.35);
        transform: translateY(-1px);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #DDE6ED;
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Inputs */
    input, select {
        background: white !important;
        border: 1.5px solid #DDE6ED !important;
        border-radius: 8px !important;
        padding: 0.65rem !important;
    }
    
    input:focus, select:focus {
        border-color: #00A3E0 !important;
        box-shadow: 0 0 0 3px rgba(0,163,224,0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# FUNCIONES
# ================================

def convertir_xlsb_a_xlsx(xlsb_file):
    """Convierte XLSB a XLSX"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsb') as tmp_xlsb:
        tmp_xlsb.write(xlsb_file.read())
        xlsb_path = tmp_xlsb.name
    
    output_dir = tempfile.gettempdir()
    
    try:
        subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'xlsx',
            '--outdir', output_dir, xlsb_path
        ], capture_output=True, timeout=60)
        
        xlsx_path = xlsb_path.replace('.xlsb', '.xlsx')
        if os.path.exists(xlsx_path):
            return xlsx_path
    except:
        pass
    finally:
        if os.path.exists(xlsb_path):
            os.remove(xlsb_path)
    
    return None


def cargar_datos(file_path):
    """Carga datos del archivo"""
    try:
        df = pd.read_excel(file_path, sheet_name='informe')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None


def formatear_moneda(valor):
    """Formatea valores monetarios"""
    if valor >= 1e9:
        return f"${valor/1e9:.1f}B"
    elif valor >= 1e6:
        return f"${valor/1e6:.1f}M"
    elif valor >= 1e3:
        return f"${valor/1e3:.1f}K"
    else:
        return f"${valor:.0f}"


def crear_grafico_dona(df, columna, titulo):
    """Crea gráfico de dona"""
    df_agrupado = df.groupby(columna)['Valor total'].sum().reset_index()
    df_agrupado = df_agrupado.sort_values('Valor total', ascending=False)
    
    colores = ['#00A3E0', '#0077B6', #00D9C8', '#4A90E2', '#00C896']
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=df_agrupado[columna],
        values=df_agrupado['Valor total'],
        hole=0.65,
        marker=dict(colors=colores, line=dict(color='white', width=2)),
        textposition='outside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.0f}<br>%{percent}<extra></extra>'
    ))
    
    total = df_agrupado['Valor total'].sum()
    fig.add_annotation(
        text=f"<b>Total</b><br>{formatear_moneda(total)}",
        x=0.5, y=0.5,
        font=dict(size=14, color='#2C3E50'),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15, color='#2C3E50'), x=0.5, xanchor='center'),
        height=420,
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, x=1.05),
        margin=dict(l=20, r=150, t=60, b=20)
    )
    
    return fig


def guardar_historico(df, mes, año, usuario):
    """Guarda informe en histórico"""
    historico_dir = "historico_informes"
    os.makedirs(historico_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{historico_dir}/informe_{mes}_{año}_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
        
        metadata = pd.DataFrame({
            'Mes': [mes],
            'Año': [año],
            'Fecha': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Usuario': [usuario],
            'Registros': [len(df)]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
    
    registro_json = f"{historico_dir}/registro.json"
    registro = []
    
    if os.path.exists(registro_json):
        with open(registro_json, 'r') as f:
            registro = json.load(f)
    
    registro.append({
        'mes': mes,
        'año': año,
        'fecha': datetime.now().isoformat(),
        'usuario': usuario,
        'archivo': filename,
        'registros': len(df)
    })
    
    with open(registro_json, 'w') as f:
        json.dump(registro, f, indent=2)
    
    return filename


def cargar_historico():
    """Carga histórico"""
    registro_json = "historico_informes/registro.json"
    if os.path.exists(registro_json):
        with open(registro_json, 'r') as f:
            return json.load(f)
    return []


# ================================
# INTERFAZ
# ================================

# Header
st.markdown("""
    <div class="header-container">
        <h1>📊 Coberturas de Inventario - Cierre de Mes</h1>
        <p>Gerencia de Energía • Sistema de Análisis de Inventarios</p>
    </div>
""", unsafe_allow_html=True)

# Barra superior
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📁 Cargar archivo de datos",
        type=['xlsx', 'xls', 'xlsb'],
        help="Formatos: XLSX, XLS, XLSB"
    )

with col2:
    mes_actual = st.selectbox(
        "Mes",
        ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        index=10  # Noviembre
    )

with col3:
    año_actual = st.number_input("Año", min_value=2020, max_value=2030, value=2024)

with col4:
    usuario = st.text_input("Usuario", value="Admin")

st.markdown("<br>", unsafe_allow_html=True)

# ================================
# PROCESAMIENTO DE DATOS
# ================================

if uploaded_file is not None:
    with st.spinner('⚡ Procesando datos...'):
        # Convertir si es XLSB
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'xlsb':
            xlsx_path = convertir_xlsb_a_xlsx(uploaded_file)
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp:
                tmp.write(uploaded_file.read())
                xlsx_path = tmp.name
        
        if xlsx_path and os.path.exists(xlsx_path):
            df = cargar_datos(xlsx_path)
            
            if df is not None and len(df) > 0:
                st.success(f"✅ Datos cargados: {len(df):,} registros • {mes_actual} {año_actual}")
                
                # ================================
                # KPIs
                # ================================
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                    referencias = df['Producto'].nunique()
                    st.markdown(f'<div class="kpi-label">🎯 REFERENCIAS</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-value">{referencias:,}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-delta">SKUs únicos</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                    stock = df['Stock'].sum()
                    st.markdown(f'<div class="kpi-label">📦 STOCK TOTAL</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-value">{stock:,.0f}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-delta">unidades</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                    valor = df['Valor total'].sum()
                    st.markdown(f'<div class="kpi-label">💰 VALOR INVENTARIO</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-value">{formatear_moneda(valor)}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-delta">${valor:,.0f}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                    if 'Rotación de Inventarios' in df.columns:
                        rotacion = df['Rotación de Inventarios'].mean()
                        st.markdown(f'<div class="kpi-label">🔄 ROTACIÓN MEDIA</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="kpi-value">{rotacion:.0f}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="kpi-delta">días promedio</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ================================
                # TABS
                # ================================
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Dashboard",
                    "📋 Datos Detallados",
                    "💾 Guardar Informe",
                    "📂 Histórico"
                ])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'Estado' in df.columns:
                            fig1 = crear_grafico_dona(df, 'Estado', '💼 Valor por Estado de Consumo')
                            st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        if 'Cobertura Inv' in df.columns:
                            fig2 = crear_grafico_dona(df, 'Cobertura Inv', '📊 Distribución por Cobertura')
                            st.plotly_chart(fig2, use_container_width=True)
                    
                    # Tabla top productos
                    st.markdown("### 🏆 Top 10 Productos por Valor")
                    df_top = df.nlargest(10, 'Valor total')[['Producto', 'Descripción', 'Stock', 'Valor total', 'Estado']]
                    st.dataframe(df_top, use_container_width=True, height=400)
                
                with tab2:
                    st.markdown("### 🔍 Filtros")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        estados = ['Todos'] + sorted(df['Estado'].unique().tolist())
                        estado_sel = st.selectbox("Estado", estados)
                    
                    with col2:
                        coberturas = ['Todos'] + sorted(df['Cobertura Inv'].unique().tolist())
                        cobertura_sel = st.selectbox("Cobertura", coberturas)
                    
                    with col3:
                        buscar = st.text_input("🔍 Buscar")
                    
                    df_filtrado = df.copy()
                    if estado_sel != 'Todos':
                        df_filtrado = df_filtrado[df_filtrado['Estado'] == estado_sel]
                    if cobertura_sel != 'Todos':
                        df_filtrado = df_filtrado[df_filtrado['Cobertura Inv'] == cobertura_sel]
                    if buscar:
                        df_filtrado = df_filtrado[df_filtrado['Descripción'].str.contains(buscar, case=False, na=False)]
                    
                    st.info(f"Mostrando {len(df_filtrado):,} de {len(df):,} registros")
                    
                    cols = ['Producto', 'Descripción', 'Stock', 'Valor total', 'Estado', 'Cobertura Inv']
                    st.dataframe(df_filtrado[cols], use_container_width=True, height=500)
                    
                    csv = df_filtrado.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Exportar CSV",
                        csv,
                        f"inventario_{mes_actual}_{año_actual}.csv",
                        "text/csv"
                    )
                
                with tab3:
                    st.markdown("### 💾 Guardar Informe Mensual")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.info(f"📅 Período: {mes_actual} {año_actual}")
                        st.info(f"👤 Usuario: {usuario}")
                        st.info(f"📊 Registros: {len(df):,}")
                    
                    with col2:
                        if st.button("💾 GUARDAR", use_container_width=True):
                            filename = guardar_historico(df, mes_actual, año_actual, usuario)
                            st.success("✅ Guardado")
                            
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    "📥 Descargar",
                                    f,
                                    f"informe_{mes_actual}_{año_actual}.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                
                with tab4:
                    st.markdown("### 📂 Histórico")
                    
                    historico = cargar_historico()
                    if historico:
                        df_hist = pd.DataFrame(historico)
                        df_hist['fecha'] = pd.to_datetime(df_hist['fecha'])
                        df_hist = df_hist.sort_values('fecha', ascending=False)
                        
                        st.dataframe(df_hist[['mes', 'año', 'fecha', 'usuario', 'registros']], use_container_width=True)
                    else:
                        st.info("No hay informes guardados")
            else:
                st.warning("No se pudieron cargar los datos")
            
            if os.path.exists(xlsx_path):
                os.remove(xlsx_path)
        else:
            st.error("Error al procesar el archivo")

else:
    st.markdown("""
        <div style='text-align: center; padding: 4rem; background: white; border-radius: 12px; border: 2px dashed #DDE6ED;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>📊</div>
            <h2 style='color: #2C3E50; margin-bottom: 1rem;'>Panel de Control de Inventarios</h2>
            <p style='color: #7F8C8D; font-size: 1.1rem;'>Carga tu archivo para comenzar el análisis</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 1rem; background: white; border-radius: 8px;'>
        <p style='color: #7F8C8D; font-size: 0.85rem; margin: 0;'>
            Dashboard Gerencia de Energía v4.0 • Sistema Enterprise
        </p>
    </div>
""", unsafe_allow_html=True)
