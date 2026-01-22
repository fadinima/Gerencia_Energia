import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
from io import BytesIO
import tempfile
import numpy as np

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
# ESTILOS CSS PREMIUM ENTERPRISE
# ================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
    
    /* Variables Enterprise */
    :root {
        --primary: #00A3E0;
        --secondary: #0077B6;
        --accent: #00D9C8;
        --success: #00C896;
        --warning: #FFB800;
        --danger: #FF6B6B;
        --dark: #1A2332;
        --gray-900: #2C3E50;
        --gray-800: #34495E;
        --gray-700: #5D6D7E;
        --gray-600: #7F8C8D;
        --gray-500: #95A5A6;
        --gray-400: #BDC3C7;
        --gray-300: #D5DBDB;
        --gray-200: #E8EBED;
        --gray-100: #F4F6F7;
        --white: #FFFFFF;
    }
    
    * {
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        margin: 0;
        padding: 0;
    }
    
    /* Background limpio */
    .main {
        background: #F8FAFB;
    }
    
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 100% !important;
    }
    
    /* Header Enterprise con logo space */
    .enterprise-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 163, 224, 0.15);
    }
    
    .header-content {
        color: white;
    }
    
    .header-content h1 {
        font-size: 1.75rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: white;
    }
    
    .header-content p {
        font-size: 0.95rem;
        opacity: 0.9;
        font-weight: 400;
        color: white;
    }
    
    .header-logo {
        background: rgba(255,255,255,0.15);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        backdrop-filter: blur(10px);
    }
    
    /* KPI Cards Premium */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.25rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--gray-200);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card:hover {
        box-shadow: 0 8px 24px rgba(0,163,224,0.12);
        transform: translateY(-2px);
        border-color: var(--primary);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
    }
    
    /* Métricas con diseño premium */
    div[data-testid="stMetricValue"] {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: var(--gray-900) !important;
        line-height: 1.2 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: var(--gray-600) !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.5rem !important;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        margin-top: 0.5rem !important;
    }
    
    /* Section Cards */
    .section-card {
        background: white;
        border-radius: 12px;
        border: 1px solid var(--gray-200);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
        overflow: hidden;
    }
    
    .section-header {
        padding: 1.25rem 1.5rem;
        background: linear-gradient(135deg, #F8FAFB 0%, #FFFFFF 100%);
        border-bottom: 1px solid var(--gray-200);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--gray-900);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-content {
        padding: 1.5rem;
    }
    
    /* Tabs Enterprise */
    .stTabs {
        background: white;
        border-radius: 12px;
        border: 1px solid var(--gray-200);
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #F8FAFB;
        border-bottom: 2px solid var(--gray-200);
        padding: 0 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: var(--gray-700);
        font-weight: 500;
        padding: 1rem 1.5rem;
        font-size: 0.9rem;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary);
        background: rgba(0,163,224,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
        background: white !important;
        font-weight: 600 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding: 1.5rem;
    }
    
    /* Filtros en una fila */
    .filter-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    
    /* Inputs Premium */
    input, select, textarea {
        background: white !important;
        border: 1.5px solid var(--gray-300) !important;
        border-radius: 8px !important;
        color: var(--gray-900) !important;
        font-size: 0.9rem !important;
        padding: 0.65rem !important;
        transition: all 0.2s ease !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0,163,224,0.1) !important;
        outline: none !important;
    }
    
    /* Botones Premium */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 1.75rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,163,224,0.2);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0,163,224,0.3);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* DataFrames Premium */
    .dataframe {
        border: none !important;
        font-size: 0.85rem !important;
    }
    
    .dataframe thead {
        background: linear-gradient(135deg, #F8FAFB 0%, #FFFFFF 100%) !important;
    }
    
    .dataframe thead th {
        color: var(--gray-900) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.5px;
        padding: 1rem 0.75rem !important;
        border-bottom: 2px solid var(--gray-300) !important;
        text-align: left !important;
    }
    
    .dataframe tbody td {
        padding: 0.85rem 0.75rem !important;
        color: var(--gray-800) !important;
        border-bottom: 1px solid var(--gray-200) !important;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(0,163,224,0.03) !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: white;
        border: 2px dashed var(--gray-300);
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary);
        background: rgba(0,163,224,0.02);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
        font-size: 0.9rem;
        padding: 0.85rem 1.25rem;
    }
    
    /* Info badges */
    .info-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.85rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background: rgba(0,163,224,0.1);
        color: var(--primary);
    }
    
    .badge-success {
        background: rgba(0,200,150,0.1);
        color: var(--success);
    }
    
    .badge-warning {
        background: rgba(255,184,0,0.1);
        color: var(--warning);
    }
    
    /* Sidebar cuando se usa */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid var(--gray-200);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-100);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gray-400);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--gray-500);
    }
    
    /* Ocultar elementos Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--primary) transparent transparent transparent !important;
    }
    
    /* Tooltips personalizados */
    .custom-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    /* Expander premium */
    .streamlit-expanderHeader {
        background: var(--gray-100);
        border-radius: 8px;
        font-weight: 600;
        color: var(--gray-900);
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# FUNCIONES AUXILIARES
# ================================

def formatear_numero(num):
    """Formatea números grandes con K, M, B"""
    if num >= 1e9:
        return f"${num/1e9:.1f}B"
    elif num >= 1e6:
        return f"${num/1e6:.1f}M"
    elif num >= 1e3:
        return f"${num/1e3:.1f}K"
    else:
        return f"${num:.0f}"


def cargar_datos_gerencia_energia(file_path, gerencia_filter="ENERGIA"):
    """Carga y filtra datos de la gerencia especificada"""
    try:
        df = pd.read_excel(file_path, sheet_name='informe')
        df.columns = df.columns.str.strip()
        
        # Filtrar por gerencia
        if 'Gerencia' in df.columns:
            df_filtered = df[df['Gerencia'].str.contains(gerencia_filter, case=False, na=False)]
        elif 'Denominación' in df.columns:
            df_filtered = df[df['Denominación'].str.contains(gerencia_filter, case=False, na=False)]
        else:
            df_filtered = df
        
        return df_filtered
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return None


def guardar_historico(df, mes, año, usuario="Sistema"):
    """Guarda el informe mensual en el histórico"""
    historico_dir = "historico_informes"
    os.makedirs(historico_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{historico_dir}/informe_{mes}_{año}_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
        
        metadata = pd.DataFrame({
            'Mes': [mes],
            'Año': [año],
            'Fecha_Generación': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Usuario': [usuario],
            'Total_Registros': [len(df)]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
    
    # Guardar registro JSON
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
    """Carga el registro histórico de informes"""
    registro_json = "historico_informes/registro.json"
    if os.path.exists(registro_json):
        with open(registro_json, 'r') as f:
            return json.load(f)
    return []


def crear_grafico_dona_premium(df, columna_grupo, columna_valor, titulo, mostrar_centro=True):
    """Crea gráfico de dona estilo Looker Studio premium"""
    
    df_agrupado = df.groupby(columna_grupo)[columna_valor].sum().reset_index()
    df_agrupado = df_agrupado.sort_values(columna_valor, ascending=False)
    
    # Paleta corporativa azul/turquesa
    colores = ['#00A3E0', '#0077B6', '#00D9C8', '#4A90E2', '#00C896', '#03DAC6', '#0288D1', '#00ACC1']
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=df_agrupado[columna_grupo],
        values=df_agrupado[columna_valor],
        hole=0.7 if mostrar_centro else 0.6,
        marker=dict(
            colors=colores[:len(df_agrupado)],
            line=dict(color='white', width=3)
        ),
        textposition='outside',
        textinfo='label+percent',
        textfont=dict(size=11, family='IBM Plex Sans', color='#2C3E50'),
        hovertemplate='<b>%{label}</b><br>' +
                     'Valor: %{value:,.0f}<br>' +
                     'Porcentaje: %{percent}<br>' +
                     '<extra></extra>',
        pull=[0.05 if i == 0 else 0 for i in range(len(df_agrupado))]
    ))
    
    # Texto central
    if mostrar_centro:
        total = df_agrupado[columna_valor].sum()
        fig.add_annotation(
            text=f"<b>Total</b><br><span style='font-size:18px'>{formatear_numero(total)}</span>",
            x=0.5, y=0.5,
            font=dict(size=13, color='#2C3E50', family='IBM Plex Sans'),
            showarrow=False,
            align='center'
        )
    
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(size=15, color='#2C3E50', family='IBM Plex Sans', weight=600),
            x=0.5,
            xanchor='center',
            y=0.98,
            yanchor='top'
        ),
        height=420,
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=10, family='IBM Plex Sans'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#E8EBED',
            borderwidth=1
        ),
        margin=dict(l=20, r=150, t=60, b=20),
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="IBM Plex Sans",
            bordercolor="#DDE6ED"
        )
    )
    
    return fig


def crear_tabla_resumen(df):
    """Crea tabla resumen tipo Looker Studio"""
    
    if 'Gerencia' in df.columns or 'Denominación' in df.columns:
        grupo_col = 'Gerencia' if 'Gerencia' in df.columns else 'Denominación'
        
        resumen = df.groupby(grupo_col).agg({
            'Producto': 'nunique',
            'Stock': 'sum',
            'Valor total': 'sum',
            'Salidas': 'sum' if 'Salidas' in df.columns else lambda x: 0
        }).reset_index()
        
        resumen.columns = ['Unidad de Negocio', 'Referencias', 'Stock', '$ Importe', 'Cant. Salidas']
        resumen = resumen.sort_values('$ Importe', ascending=False)
        
        # Formatear números
        resumen['Stock'] = resumen['Stock'].apply(lambda x: f"{x:,.0f}")
        resumen['$ Importe'] = resumen['$ Importe'].apply(lambda x: f"${x:,.0f}")
        resumen['Cant. Salidas'] = resumen['Cant. Salidas'].apply(lambda x: f"{x:,.0f}")
        
        return resumen
    
    return pd.DataFrame()


# ================================
# INTERFAZ PRINCIPAL
# ================================

# Header Enterprise
st.markdown("""
    <div class="enterprise-header">
        <div class="header-content">
            <h1>📊 Coberturas de Inventario - Cierre de Mes</h1>
            <p>Gerencia de Energía • Panel de Control Ejecutivo</p>
        </div>
        <div class="header-logo">
            ⚡ ENERGÍA
        </div>
    </div>
""", unsafe_allow_html=True)

# Barra de configuración superior
col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])

with col1:
    uploaded_file = st.file_uploader(
        "📁 Cargar archivo de datos",
        type=['xlsx', 'xls', 'xlsb'],
        help="Formatos: XLSX, XLS, XLSB"
    )

with col2:
    mes_actual = st.selectbox(
        "📅 Mes",
        ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        index=datetime.now().month - 1
    )

with col3:
    año_actual = st.number_input(
        "📆 Año",
        min_value=2020,
        max_value=2030,
        value=datetime.now().year
    )

with col4:
    usuario = st.text_input("👤 Usuario", value="Admin")

with col5:
    gerencia_filter = st.text_input("🔍 Filtro Gerencia", value="ENERGIA")

st.markdown("<br>", unsafe_allow_html=True)

# ================================
# CONTENIDO PRINCIPAL
# ================================

if uploaded_file is not None:
    with st.spinner('⚡ Procesando datos...'):
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.read())
            xlsx_path = tmp_file.name
        
        df = cargar_datos_gerencia_energia(xlsx_path, gerencia_filter)
        
        if df is not None and len(df) > 0:
            
            # Mensaje de éxito
            st.success(f"✅ Datos cargados exitosamente • {len(df):,} registros • {mes_actual} {año_actual}")
            
            # ================================
            # KPIs PRINCIPALES
            # ================================
            
            st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                referencias = df['Producto'].nunique() if 'Producto' in df.columns else len(df)
                st.metric("🎯 REFERENCIAS", f"{referencias:,}", "SKUs únicos")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                stock = df['Stock'].sum() if 'Stock' in df.columns else 0
                st.metric("📦 STOCK TOTAL", f"{stock:,.0f}", "unidades")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                valor = df['Valor total'].sum() if 'Valor total' in df.columns else 0
                st.metric("💰 VALOR INVENTARIO", formatear_numero(valor), f"${valor:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
                if 'Rotación de Inventarios' in df.columns:
                    rotacion = df['Rotación de Inventarios'].mean()
                    st.metric("🔄 ROTACIÓN MEDIA", f"{rotacion:.0f}", "días promedio")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ================================
            # TABS PRINCIPALES
            # ================================
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Dashboard Ejecutivo",
                "📋 Análisis Detallado",
                "📈 Reportes y Exportación",
                "📂 Histórico"
            ])
            
            # TAB 1: DASHBOARD EJECUTIVO
            with tab1:
                
                # Fila 1: Gráficos de dona
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'Estado' in df.columns and 'Valor total' in df.columns:
                        fig1 = crear_grafico_dona_premium(
                            df, 'Estado', 'Valor total',
                            '💼 Valor de Inventario por Estado de Consumo'
                        )
                        st.plotly_chart(fig1, use_container_width=True, key="dona1")
                
                with col2:
                    if 'Cobertura Inv' in df.columns and 'Valor total' in df.columns:
                        fig2 = crear_grafico_dona_premium(
                            df, 'Cobertura Inv', 'Valor total',
                            '📊 Distribución por Cobertura de Inventario'
                        )
                        st.plotly_chart(fig2, use_container_width=True, key="dona2")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Tabla resumen
                st.markdown("### 📋 Resumen por Unidad de Negocio")
                tabla_resumen = crear_tabla_resumen(df)
                if not tabla_resumen.empty:
                    st.dataframe(tabla_resumen, use_container_width=True, height=300)
            
            # TAB 2: ANÁLISIS DETALLADO
            with tab2:
                
                # Filtros en fila
                st.markdown("### 🔍 Filtros de Análisis")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'Estado' in df.columns:
                        estados = ['Todos'] + sorted(df['Estado'].unique().tolist())
                        estado_sel = st.selectbox("Estado de Consumo", estados, key="filtro_estado")
                
                with col2:
                    if 'Cobertura Inv' in df.columns:
                        coberturas = ['Todos'] + sorted(df['Cobertura Inv'].unique().tolist())
                        cobertura_sel = st.selectbox("Cobertura", coberturas, key="filtro_cob")
                
                with col3:
                    buscar = st.text_input("🔍 Buscar producto", key="buscar_prod")
                
                # Aplicar filtros
                df_filtrado = df.copy()
                if estado_sel != 'Todos':
                    df_filtrado = df_filtrado[df_filtrado['Estado'] == estado_sel]
                if cobertura_sel != 'Todos':
                    df_filtrado = df_filtrado[df_filtrado['Cobertura Inv'] == cobertura_sel]
                if buscar:
                    df_filtrado = df_filtrado[df_filtrado['Descripción'].str.contains(buscar, case=False, na=False)]
                
                # Info de registros
                st.info(f"📊 Mostrando **{len(df_filtrado):,}** de **{len(df):,}** registros")
                
                # Seleccionar columnas a mostrar
                columnas_disponibles = df_filtrado.columns.tolist()
                columnas_principales = []
                
                for col in ['Producto', 'Descripción', 'Centro', 'Almacen', 'Stock', 'Valor total', 
                           'Estado', 'Cobertura Inv', 'Rotación de Inventarios']:
                    if col in columnas_disponibles:
                        columnas_principales.append(col)
                
                # Tabla interactiva
                st.markdown("### 📊 Tabla de Datos")
                st.dataframe(
                    df_filtrado[columnas_principales],
                    use_container_width=True,
                    height=500
                )
                
                # Botón de descarga
                csv = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Descargar datos filtrados (CSV)",
                    csv,
                    f"inventario_filtrado_{mes_actual}_{año_actual}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            # TAB 3: REPORTES
            with tab3:
                
                st.markdown("### 💾 Guardar Informe Mensual")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background: #F8FAFB; padding: 1.5rem; border-radius: 8px; border: 1px solid #E8EBED;'>
                        <p style='margin: 0 0 0.5rem 0; color: #7F8C8D; font-size: 0.85rem; font-weight: 600;'>INFORMACIÓN DEL INFORME</p>
                        <p style='margin: 0.25rem 0; color: #2C3E50;'><strong>Período:</strong> {mes_actual} {año_actual}</p>
                        <p style='margin: 0.25rem 0; color: #2C3E50;'><strong>Usuario:</strong> {usuario}</p>
                        <p style='margin: 0.25rem 0; color: #2C3E50;'><strong>Registros:</strong> {len(df):,}</p>
                        <p style='margin: 0.25rem 0; color: #2C3E50;'><strong>Gerencia:</strong> {gerencia_filter}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("💾 GUARDAR INFORME", use_container_width=True, type="primary"):
                        with st.spinner('Guardando...'):
                            filename = guardar_historico(df, mes_actual, año_actual, usuario)
                            st.success(f"✅ Informe guardado exitosamente")
                            
                            # Botón de descarga
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    "📥 Descargar Informe Excel",
                                    f,
                                    f"informe_{mes_actual}_{año_actual}.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Opciones de exportación adicionales
                st.markdown("### 📤 Exportar Datos")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV completo
                    csv_completo = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📄 Exportar todos los datos (CSV)",
                        csv_completo,
                        f"inventario_completo_{mes_actual}_{año_actual}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Resumen
                    tabla_resumen = crear_tabla_resumen(df)
                    if not tabla_resumen.empty:
                        csv_resumen = tabla_resumen.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📊 Exportar resumen (CSV)",
                            csv_resumen,
                            f"resumen_{mes_actual}_{año_actual}.csv",
                            "text/csv",
                            use_container_width=True
                        )
            
            # TAB 4: HISTÓRICO
            with tab4:
                
                st.markdown("### 📂 Histórico de Informes Generados")
                
                historico = cargar_historico()
                
                if historico:
                    df_hist = pd.DataFrame(historico)
                    df_hist['fecha'] = pd.to_datetime(df_hist['fecha'])
                    df_hist = df_hist.sort_values('fecha', ascending=False)
                    
                    # Mostrar tabla
                    st.dataframe(
                        df_hist[['mes', 'año', 'fecha', 'usuario', 'registros']],
                        use_container_width=True,
                        height=400
                    )
                    
                    # Gráfico de evolución
                    if len(df_hist) > 1:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("### 📈 Evolución de Registros")
                        
                        fig_evol = go.Figure()
                        fig_evol.add_trace(go.Scatter(
                            x=df_hist['fecha'],
                            y=df_hist['registros'],
                            mode='lines+markers',
                            line=dict(color='#00A3E0', width=3),
                            marker=dict(size=10, color='#0077B6', line=dict(color='white', width=2)),
                            hovertemplate='<b>%{x|%B %Y}</b><br>Registros: %{y:,}<extra></extra>'
                        ))
                        
                        fig_evol.update_layout(
                            height=350,
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(family='IBM Plex Sans', size=12, color='#2C3E50'),
                            xaxis=dict(
                                title='Fecha',
                                gridcolor='#F0F0F0',
                                showgrid=True
                            ),
                            yaxis=dict(
                                title='Número de Registros',
                                gridcolor='#F0F0F0',
                                showgrid=True
                            ),
                            margin=dict(l=40, r=40, t=20, b=40),
                            hoverlabel=dict(bgcolor="white", font_size=11, bordercolor="#DDE6ED")
                        )
                        
                        st.plotly_chart(fig_evol, use_container_width=True)
                else:
                    st.info("📭 No hay informes guardados en el histórico")
        
        else:
            st.warning(f"⚠️ No se encontraron datos para la gerencia '{gerencia_filter}'")
        
        # Limpiar archivo temporal
        if os.path.exists(xlsx_path):
            os.remove(xlsx_path)

else:
    # Pantalla de bienvenida
    st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; background: white; border-radius: 12px; border: 2px dashed #DDE6ED; margin-top: 2rem;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>📊</div>
            <h2 style='color: #2C3E50; margin-bottom: 1rem; font-weight: 600;'>Panel de Control de Inventarios</h2>
            <p style='color: #7F8C8D; font-size: 1.1rem; margin-bottom: 2rem;'>
                Carga tu archivo de datos para comenzar el análisis
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; max-width: 800px; margin: 0 auto;'>
                <div style='padding: 1.5rem; background: #F8FAFB; border-radius: 8px; border: 1px solid #E8EBED;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>⚡</div>
                    <div style='font-weight: 600; color: #2C3E50; margin-bottom: 0.25rem;'>Análisis Rápido</div>
                    <div style='font-size: 0.85rem; color: #7F8C8D;'>Procesamiento instantáneo</div>
                </div>
                <div style='padding: 1.5rem; background: #F8FAFB; border-radius: 8px; border: 1px solid #E8EBED;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📊</div>
                    <div style='font-weight: 600; color: #2C3E50; margin-bottom: 0.25rem;'>Visualización Premium</div>
                    <div style='font-size: 0.85rem; color: #7F8C8D;'>Gráficos interactivos</div>
                </div>
                <div style='padding: 1.5rem; background: #F8FAFB; border-radius: 8px; border: 1px solid #E8EBED;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>💾</div>
                    <div style='font-weight: 600; color: #2C3E50; margin-bottom: 0.25rem;'>Histórico Completo</div>
                    <div style='font-size: 0.85rem; color: #7F8C8D;'>Control de versiones</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: white; border-radius: 8px; border: 1px solid #E8EBED;'>
        <p style='margin: 0; color: #7F8C8D; font-size: 0.85rem;'>
            <strong>Dashboard Gerencia de Energía</strong> • Sistema Enterprise v3.0 • Powered by Streamlit & AI
        </p>
    </div>
""", unsafe_allow_html=True)
