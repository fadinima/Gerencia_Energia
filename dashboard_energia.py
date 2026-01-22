import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
from io import BytesIO
import tempfile

# ================================
# CONFIGURACIÓN DE LA PÁGINA
# ================================
st.set_page_config(
    page_title="Dashboard Gerencia de Energía",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# ESTILOS CSS MODERNOS Y ATRACTIVOS
# ================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    /* Variables de color - Esquema energético vibrante */
    :root {
        --primary: #FF6B35;
        --secondary: #F7931E;
        --accent: #FDC830;
        --dark: #1A1A2E;
        --light: #EAEAEA;
        --success: #4ECDC4;
        --danger: #FF6B6B;
        --info: #4D96FF;
    }
    
    /* Fuente global */
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Fondo con patrón */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
        position: relative;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,.03) 35px, rgba(255,255,255,.03) 70px);
        pointer-events: none;
        z-index: 0;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        position: relative;
        z-index: 1;
    }
    
    /* Header espectacular con gradiente y efectos */
    .hero-header {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FDC830 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 60px rgba(255, 107, 53, 0.3),
            0 0 0 1px rgba(255,255,255,0.1) inset;
        position: relative;
        overflow: hidden;
        animation: slideDown 0.6s ease-out;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-header h1 {
        margin: 0;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
        letter-spacing: -1px;
    }
    
    .hero-header p {
        margin: 1rem 0 0 0;
        font-size: 1.3rem;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Tarjetas de métricas modernas */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255,255,255,0.5) inset;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out backwards;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(255,255,255,0.8) inset;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #FF6B35, #F7931E, #FDC830);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Animaciones escalonadas */
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    
    /* Valores de métricas con estilo */
    div[data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #555 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar elegante */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A2E 0%, #16213E 100%);
        border-right: 2px solid rgba(255, 107, 53, 0.3);
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Botones modernos */
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #F7931E 0%, #FF6B35 100%);
        box-shadow: 0 6px 25px rgba(255, 107, 53, 0.5);
        transform: translateY(-2px);
    }
    
    /* Tabs elegantes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B35, #F7931E) !important;
        color: white !important;
    }
    
    /* Inputs y selectboxes */
    .stSelectbox, .stTextInput, .stNumberInput {
        color: white;
    }
    
    input, select {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 0.75rem !important;
    }
    
    /* File uploader elegante */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(255, 107, 53, 0.5);
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #FF6B35;
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Dataframes con estilo */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Alertas personalizadas */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Success messages */
    .element-container:has(.stSuccess) {
        animation: bounceIn 0.6s ease-out;
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Spinner personalizado */
    .stSpinner > div {
        border-color: #FF6B35 transparent transparent transparent !important;
    }
    
    /* Footer moderno */
    .footer {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Efectos de brillo en hover para gráficos */
    .js-plotly-plot:hover {
        filter: brightness(1.05);
        transition: filter 0.3s ease;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #F7931E, #FDC830);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.35em 0.65em;
        font-size: 0.875em;
        font-weight: 600;
        line-height: 1;
        color: #fff;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# FUNCIONES AUXILIARES
# ================================

def cargar_datos_gerencia_energia(file_path, gerencia_filter="ENERGIA"):
    """Carga y filtra datos de la gerencia especificada"""
    try:
        df = pd.read_excel(file_path, sheet_name='informe')
        df.columns = df.columns.str.strip()
        
        if 'Gerencia' in df.columns:
            df_filtered = df[df['Gerencia'].str.contains(gerencia_filter, case=False, na=False)]
        elif 'Denominación' in df.columns:
            df_filtered = df[df['Denominación'].str.contains(gerencia_filter, case=False, na=False)]
        else:
            df_filtered = df
        
        return df_filtered
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
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


def crear_graficos_modernos(df):
    """Crea gráficos modernos y atractivos con Plotly"""
    graficos = {}
    
    # Paleta de colores vibrante
    color_scale = ['#FF6B35', '#F7931E', '#FDC830', '#4ECDC4', '#4D96FF', '#764ba2']
    
    # 1. Valor total por estado - Gráfico de barras horizontal con gradiente
    if 'Estado' in df.columns and 'Valor total' in df.columns:
        df_estado = df.groupby('Estado')['Valor total'].sum().reset_index()
        df_estado = df_estado.sort_values('Valor total', ascending=True)
        
        fig_estado = go.Figure()
        fig_estado.add_trace(go.Bar(
            y=df_estado['Estado'],
            x=df_estado['Valor total'],
            orientation='h',
            marker=dict(
                color=df_estado['Valor total'],
                colorscale=[[0, '#FF6B35'], [0.5, '#F7931E'], [1, '#FDC830']],
                line=dict(color='rgba(255,255,255,0.3)', width=2)
            ),
            text=[f'${val:,.0f}' for val in df_estado['Valor total']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Valor: $%{x:,.0f}<extra></extra>'
        ))
        
        fig_estado.update_layout(
            title={
                'text': '💰 Valor Total de Inventario por Estado',
                'font': {'size': 24, 'family': 'Poppins', 'color': 'white', 'weight': 700}
            },
            xaxis_title='Valor Total ($)',
            yaxis_title='',
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.05)',
            font=dict(color='white', family='Poppins'),
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        graficos['estado'] = fig_estado
    
    # 2. Distribución por cobertura - Donut chart moderno
    if 'Cobertura Inv' in df.columns and 'Valor total' in df.columns:
        df_cobertura = df.groupby('Cobertura Inv')['Valor total'].sum().reset_index()
        
        fig_cobertura = go.Figure()
        fig_cobertura.add_trace(go.Pie(
            labels=df_cobertura['Cobertura Inv'],
            values=df_cobertura['Valor total'],
            hole=0.6,
            marker=dict(
                colors=color_scale,
                line=dict(color='white', width=3)
            ),
            textposition='outside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.0f}<br>%{percent}<extra></extra>'
        ))
        
        fig_cobertura.update_layout(
            title={
                'text': '📊 Distribución por Cobertura de Inventario',
                'font': {'size': 24, 'family': 'Poppins', 'color': 'white', 'weight': 700}
            },
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Poppins', size=12),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                bgcolor='rgba(255,255,255,0.1)',
                bordercolor='rgba(255,255,255,0.3)',
                borderwidth=1
            )
        )
        graficos['cobertura'] = fig_cobertura
    
    # 3. Top 10 productos - Gráfico de barras con sombras
    if 'Descripción' in df.columns and 'Valor total' in df.columns:
        df_top = df.nlargest(10, 'Valor total')[['Descripción', 'Valor total', 'Stock']].copy()
        df_top['Descripción'] = df_top['Descripción'].str[:40] + '...'
        df_top = df_top.sort_values('Valor total', ascending=True)
        
        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            y=df_top['Descripción'],
            x=df_top['Valor total'],
            orientation='h',
            marker=dict(
                color=df_top['Valor total'],
                colorscale='Sunset',
                line=dict(color='rgba(255,255,255,0.3)', width=2)
            ),
            text=[f'${val:,.0f}' for val in df_top['Valor total']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Valor: $%{x:,.0f}<extra></extra>'
        ))
        
        fig_top.update_layout(
            title={
                'text': '🏆 Top 10 Productos por Valor Total',
                'font': {'size': 24, 'family': 'Poppins', 'color': 'white', 'weight': 700}
            },
            xaxis_title='Valor Total ($)',
            yaxis_title='',
            height=550,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.05)',
            font=dict(color='white', family='Poppins'),
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        graficos['top_productos'] = fig_top
    
    # 4. Rotación de inventarios - Histograma con línea de densidad
    if 'Rotación de Inventarios' in df.columns:
        fig_rotacion = go.Figure()
        fig_rotacion.add_trace(go.Histogram(
            x=df['Rotación de Inventarios'],
            nbinsx=40,
            marker=dict(
                color='#FF6B35',
                line=dict(color='white', width=1)
            ),
            hovertemplate='Rotación: %{x:.1f} días<br>Frecuencia: %{y}<extra></extra>'
        ))
        
        fig_rotacion.update_layout(
            title={
                'text': '🔄 Distribución de Rotación de Inventarios',
                'font': {'size': 24, 'family': 'Poppins', 'color': 'white', 'weight': 700}
            },
            xaxis_title='Rotación (días)',
            yaxis_title='Frecuencia',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.05)',
            font=dict(color='white', family='Poppins'),
            showlegend=False,
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        graficos['rotacion'] = fig_rotacion
    
    return graficos


# ================================
# HEADER ESPECTACULAR
# ================================
st.markdown("""
    <div class="hero-header">
        <h1>⚡ Dashboard Gerencia de Energía</h1>
        <p>Sistema Inteligente de Análisis de Inventarios • Control Mensual Automatizado</p>
    </div>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR ELEGANTE
# ================================
with st.sidebar:
    st.markdown("### 🔥 LOGO EMPRESA")
    st.image("https://via.placeholder.com/300x100/FF6B35/FFFFFF?text=TU+LOGO", 
             use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📁 CARGA DE ARCHIVO")
    
    uploaded_file = st.file_uploader(
        "Arrastra o selecciona tu archivo",
        type=['xlsx', 'xls', 'xlsb'],
        help="Formatos soportados: XLSX, XLS, XLSB"
    )
    
    st.markdown("---")
    st.markdown("### 📅 PERÍODO DEL INFORME")
    
    col1, col2 = st.columns(2)
    with col1:
        mes_actual = st.selectbox(
            "Mes",
            ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
            index=datetime.now().month - 1
        )
    with col2:
        año_actual = st.number_input(
            "Año",
            min_value=2020,
            max_value=2030,
            value=datetime.now().year
        )
    
    st.markdown("---")
    st.markdown("### 👤 USUARIO")
    usuario = st.text_input("Nombre", value="Administrador")
    
    st.markdown("---")
    st.markdown("### 🔍 FILTROS")
    gerencia_filter = st.text_input(
        "Gerencia",
        value="ENERGIA",
        help="Ingresa el nombre de la gerencia a analizar"
    )
    
    st.markdown("---")
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 10px;'>
            <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>Dashboard v2.0 Pro</p>
            <p style='margin: 0; font-size: 0.8rem; opacity: 0.6;'>Powered by Streamlit</p>
        </div>
    """, unsafe_allow_html=True)

# ================================
# CONTENIDO PRINCIPAL
# ================================

if uploaded_file is not None:
    with st.spinner('⚡ Procesando datos...'):
        # Guardar archivo temporalmente
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.read())
            xlsx_path = tmp_file.name
        
        # Cargar datos
        df = cargar_datos_gerencia_energia(xlsx_path, gerencia_filter)
        
        if df is not None and len(df) > 0:
            st.success(f"✅ ¡Perfecto! Cargados {len(df):,} registros de {gerencia_filter}")
            
            # ================================
            # MÉTRICAS PRINCIPALES CON ANIMACIÓN
            # ================================
            st.markdown("### 📊 Panel de Control Principal")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_productos = df['Producto'].nunique() if 'Producto' in df.columns else len(df)
                st.metric(
                    label="🎯 Productos Únicos",
                    value=f"{total_productos:,}",
                    delta="SKUs activos"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_stock = df['Stock'].sum() if 'Stock' in df.columns else 0
                st.metric(
                    label="📦 Stock Total",
                    value=f"{total_stock:,.0f}",
                    delta="Unidades"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_valor = df['Valor total'].sum() if 'Valor total' in df.columns else 0
                st.metric(
                    label="💵 Valor Inventario",
                    value=f"${total_valor/1e6:.1f}M",
                    delta=f"${total_valor:,.0f}"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                if 'Rotación de Inventarios' in df.columns:
                    rotacion_promedio = df['Rotación de Inventarios'].mean()
                    st.metric(
                        label="🔄 Rotación Media",
                        value=f"{rotacion_promedio:.0f}",
                        delta="Días"
                    )
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ================================
            # TABS MODERNOS
            # ================================
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Análisis Visual", 
                "📋 Datos Detallados", 
                "💾 Guardar Informe",
                "📂 Histórico",
                "ℹ️ Información"
            ])
            
            with tab1:
                st.markdown("### 📈 Visualizaciones Interactivas")
                
                graficos = crear_graficos_modernos(df)
                
                if 'estado' in graficos or 'cobertura' in graficos:
                    col1, col2 = st.columns(2)
                    with col1:
                        if 'estado' in graficos:
                            st.plotly_chart(graficos['estado'], use_container_width=True, key="estado")
                    with col2:
                        if 'cobertura' in graficos:
                            st.plotly_chart(graficos['cobertura'], use_container_width=True, key="cobertura")
                
                if 'top_productos' in graficos:
                    st.plotly_chart(graficos['top_productos'], use_container_width=True, key="top")
                
                if 'rotacion' in graficos:
                    st.plotly_chart(graficos['rotacion'], use_container_width=True, key="rotacion")
            
            with tab2:
                st.markdown("### 📋 Explorador de Datos")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if 'Estado' in df.columns:
                        estados = ['Todos'] + sorted(list(df['Estado'].unique()))
                        estado_filter = st.selectbox("🎯 Estado", estados)
                with col2:
                    if 'Cobertura Inv' in df.columns:
                        coberturas = ['Todos'] + sorted(list(df['Cobertura Inv'].unique()))
                        cobertura_filter = st.selectbox("📊 Cobertura", coberturas)
                with col3:
                    buscar = st.text_input("🔍 Buscar producto", "")
                
                df_display = df.copy()
                if estado_filter != 'Todos':
                    df_display = df_display[df_display['Estado'] == estado_filter]
                if cobertura_filter != 'Todos':
                    df_display = df_display[df_display['Cobertura Inv'] == cobertura_filter]
                if buscar:
                    df_display = df_display[df_display['Descripción'].str.contains(buscar, case=False, na=False)]
                
                st.info(f"📊 Mostrando {len(df_display):,} de {len(df):,} registros")
                st.dataframe(df_display, use_container_width=True, height=500)
                
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"energia_{mes_actual}_{año_actual}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with tab3:
                st.markdown("### 💾 Guardar Informe Mensual")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.info(f"📅 **Período:** {mes_actual} {año_actual}")
                    st.info(f"👤 **Usuario:** {usuario}")
                    st.info(f"📊 **Registros:** {len(df):,}")
                
                with col2:
                    if st.button("💾 GUARDAR", type="primary", use_container_width=True):
                        with st.spinner('Guardando...'):
                            filename = guardar_historico(df, mes_actual, año_actual, usuario)
                            st.success(f"✅ ¡Guardado! {filename}")
                            
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    label="📥 Descargar",
                                    data=f,
                                    file_name=f"informe_{mes_actual}_{año_actual}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
            
            with tab4:
                st.markdown("### 📂 Histórico de Informes")
                
                historico = cargar_historico()
                
                if historico:
                    df_historico = pd.DataFrame(historico)
                    df_historico['fecha'] = pd.to_datetime(df_historico['fecha'])
                    df_historico = df_historico.sort_values('fecha', ascending=False)
                    
                    st.dataframe(
                        df_historico[['mes', 'año', 'fecha', 'usuario', 'registros']],
                        use_container_width=True,
                        height=400
                    )
                    
                    if len(df_historico) > 1:
                        fig = px.line(
                            df_historico,
                            x='fecha',
                            y='registros',
                            markers=True,
                            title='📈 Evolución Histórica'
                        )
                        fig.update_traces(line_color='#FF6B35', marker_size=10)
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(255,255,255,0.05)',
                            font=dict(color='white')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("📭 No hay informes guardados")
            
            with tab5:
                st.markdown("### ℹ️ Guía Rápida")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    #### 🚀 Flujo de Trabajo
                    
                    1. **Cargar archivo** XLSX/XLSB
                    2. **Revisar métricas** principales
                    3. **Explorar gráficos** interactivos
                    4. **Filtrar datos** específicos
                    5. **Guardar informe** mensual
                    6. **Consultar histórico**
                    """)
                
                with col2:
                    st.markdown("""
                    #### 💡 Tips de Uso
                    
                    - 🎨 Gráficos interactivos: zoom, pan, hover
                    - 📊 Filtros dinámicos en tiempo real
                    - 💾 Histórico automático por mes
                    - 📥 Exporta a CSV o Excel
                    - 🔍 Búsqueda rápida de productos
                    - 📈 Comparativas mensuales
                    """)
        else:
            st.warning(f"⚠️ No se encontraron datos para '{gerencia_filter}'")
        
        if os.path.exists(xlsx_path):
            os.remove(xlsx_path)
else:
    # Pantalla de bienvenida moderna
    st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; background: rgba(255,255,255,0.05); border-radius: 20px; border: 2px dashed rgba(255,107,53,0.5);'>
            <h2 style='color: white; font-size: 2.5rem; margin-bottom: 1rem;'>👋 ¡Bienvenido!</h2>
            <p style='color: rgba(255,255,255,0.8); font-size: 1.3rem; margin-bottom: 2rem;'>
                Carga tu archivo para comenzar el análisis
            </p>
            <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;'>
                <div style='background: rgba(255,107,53,0.1); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,107,53,0.3); flex: 1; min-width: 200px;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📁</div>
                    <div style='color: white; font-weight: 600;'>Carga Rápida</div>
                    <div style='color: rgba(255,255,255,0.6); font-size: 0.9rem;'>XLSX, XLS, XLSB</div>
                </div>
                <div style='background: rgba(247,147,30,0.1); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(247,147,30,0.3); flex: 1; min-width: 200px;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>⚡</div>
                    <div style='color: white; font-weight: 600;'>Análisis Instantáneo</div>
                    <div style='color: rgba(255,255,255,0.6); font-size: 0.9rem;'>Resultados en segundos</div>
                </div>
                <div style='background: rgba(253,200,48,0.1); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(253,200,48,0.3); flex: 1; min-width: 200px;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📊</div>
                    <div style='color: white; font-weight: 600;'>Visualización Pro</div>
                    <div style='color: rgba(255,255,255,0.6); font-size: 0.9rem;'>Gráficos interactivos</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ================================
# FOOTER MODERNO
# ================================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <div style='font-size: 1.5rem; margin-bottom: 1rem;'>⚡</div>
        <div style='color: white; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;'>
            Dashboard Gerencia de Energía
        </div>
        <div style='color: rgba(255,255,255,0.6); font-size: 0.9rem;'>
            Sistema Profesional de Análisis v2.0 • Desarrollado con ❤️ usando Streamlit & Python
        </div>
        <div style='color: rgba(255,255,255,0.4); font-size: 0.8rem; margin-top: 1rem;'>
            © 2026 Tu Empresa - Todos los derechos reservados
        </div>
    </div>
""", unsafe_allow_html=True)
