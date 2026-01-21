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
    page_title="Dashboard Gerencia de Energía",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# ESTILOS CSS PERSONALIZADOS
# ================================
st.markdown("""
    <style>
    /* Colores corporativos - PERSONALIZAR AQUÍ */
    :root {
        --primary-color: #1E40AF;
        --secondary-color: #3B82F6;
        --accent-color: #60A5FA;
        --background-color: #F0F4F8;
    }
    
    /* Header personalizado */
    .main-header {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Métricas personalizadas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3B82F6;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F8FAFC;
    }
    
    /* Botones */
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #1E40AF;
    }
    
    /* Tablas */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Alertas de estado */
    .alert-success {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #10B981;
    }
    
    .alert-warning {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #F59E0B;
    }
    
    .alert-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #EF4444;
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# FUNCIONES AUXILIARES
# ================================

def convertir_xlsb_a_xlsx(xlsb_file):
    """Convierte archivo XLSB a XLSX usando LibreOffice"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsb') as tmp_xlsb:
        tmp_xlsb.write(xlsb_file.read())
        xlsb_path = tmp_xlsb.name
    
    output_dir = tempfile.gettempdir()
    
    try:
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'xlsx',
            '--outdir', output_dir, xlsb_path
        ], capture_output=True, text=True, timeout=60)
        
        xlsx_path = xlsb_path.replace('.xlsb', '.xlsx')
        
        if os.path.exists(xlsx_path):
            return xlsx_path
        else:
            st.error("Error al convertir el archivo XLSB")
            return None
    except Exception as e:
        st.error(f"Error en la conversión: {e}")
        return None
    finally:
        if os.path.exists(xlsb_path):
            os.remove(xlsb_path)


def cargar_datos_gerencia_energia(file_path, gerencia_filter="ENERGIA"):
    """Carga y filtra datos de la gerencia especificada"""
    try:
        # Leer la hoja 'informe' que tiene todos los datos
        df = pd.read_excel(file_path, sheet_name='informe')
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Filtrar por gerencia (si existe la columna)
        if 'Gerencia' in df.columns:
            df_filtered = df[df['Gerencia'].str.contains(gerencia_filter, case=False, na=False)]
        elif 'Denominación' in df.columns:
            df_filtered = df[df['Denominación'].str.contains(gerencia_filter, case=False, na=False)]
        else:
            # Si no hay columna de gerencia, tomar todos los datos
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
    
    # Guardar Excel con metadata
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
        
        # Crear hoja de metadata
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


def crear_graficos_analisis(df):
    """Crea gráficos de análisis para el dashboard"""
    graficos = {}
    
    # 1. Valor total por estado
    if 'Estado' in df.columns and 'Valor total' in df.columns:
        df_estado = df.groupby('Estado')['Valor total'].sum().reset_index()
        df_estado = df_estado.sort_values('Valor total', ascending=False)
        
        fig_estado = px.bar(
            df_estado, 
            x='Estado', 
            y='Valor total',
            title='Valor Total de Inventario por Estado de Consumo',
            labels={'Valor total': 'Valor Total ($)', 'Estado': 'Estado'},
            color='Valor total',
            color_continuous_scale='Blues'
        )
        fig_estado.update_layout(showlegend=False, height=400)
        graficos['estado'] = fig_estado
    
    # 2. Distribución por cobertura
    if 'Cobertura Inv' in df.columns and 'Valor total' in df.columns:
        df_cobertura = df.groupby('Cobertura Inv')['Valor total'].sum().reset_index()
        
        fig_cobertura = px.pie(
            df_cobertura,
            values='Valor total',
            names='Cobertura Inv',
            title='Distribución de Valor por Cobertura de Inventario',
            hole=0.4
        )
        fig_cobertura.update_layout(height=400)
        graficos['cobertura'] = fig_cobertura
    
    # 3. Top 10 productos por valor
    if 'Descripción' in df.columns and 'Valor total' in df.columns:
        df_top = df.nlargest(10, 'Valor total')[['Descripción', 'Valor total', 'Stock']]
        
        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            y=df_top['Descripción'],
            x=df_top['Valor total'],
            orientation='h',
            marker=dict(color='#3B82F6'),
            text=df_top['Stock'],
            texttemplate='Stock: %{text}',
            textposition='auto'
        ))
        fig_top.update_layout(
            title='Top 10 Productos por Valor Total',
            xaxis_title='Valor Total ($)',
            yaxis_title='Producto',
            height=500
        )
        graficos['top_productos'] = fig_top
    
    # 4. Rotación de inventarios
    if 'Rotación de Inventarios' in df.columns:
        fig_rotacion = px.histogram(
            df,
            x='Rotación de Inventarios',
            nbins=30,
            title='Distribución de Rotación de Inventarios',
            labels={'Rotación de Inventarios': 'Rotación (días)'},
            color_discrete_sequence=['#3B82F6']
        )
        fig_rotacion.update_layout(height=400)
        graficos['rotacion'] = fig_rotacion
    
    return graficos


# ================================
# HEADER CORPORATIVO
# ================================
st.markdown("""
    <div class="main-header">
        <h1>⚡ Dashboard Gerencia de Energía</h1>
        <p>Sistema de Análisis de Inventarios y Coberturas - Control Mensual</p>
    </div>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR - CONFIGURACIÓN
# ================================
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1E40AF/FFFFFF?text=LOGO+EMPRESA", 
             use_container_width=True)
    
    st.markdown("### 📁 Carga de Archivo")
    
    uploaded_file = st.file_uploader(
        "Selecciona el archivo XLSB",
        type=['xlsb'],
        help="Sube el informe mensual en formato XLSB"
    )
    
    st.markdown("---")
    
    # Configuración del mes
    st.markdown("### 📅 Período del Informe")
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
    
    # Usuario
    st.markdown("### 👤 Usuario")
    usuario = st.text_input("Nombre", value="Administrador")
    
    st.markdown("---")
    
    # Filtro de gerencia
    st.markdown("### 🔍 Filtros")
    gerencia_filter = st.text_input(
        "Gerencia a analizar",
        value="ENERGIA",
        help="Ingresa el nombre de la gerencia"
    )

# ================================
# CONTENIDO PRINCIPAL
# ================================

if uploaded_file is not None:
    with st.spinner('⏳ Procesando archivo XLSB...'):
        # Convertir XLSB a XLSX
        xlsx_path = convertir_xlsb_a_xlsx(uploaded_file)
        
        if xlsx_path:
            # Cargar datos filtrados
            df = cargar_datos_gerencia_energia(xlsx_path, gerencia_filter)
            
            if df is not None and len(df) > 0:
                st.success(f"✅ Archivo cargado exitosamente. Registros encontrados: {len(df)}")
                
                # ================================
                # MÉTRICAS PRINCIPALES
                # ================================
                st.markdown("### 📊 Resumen Ejecutivo")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_productos = df['Producto'].nunique() if 'Producto' in df.columns else len(df)
                    st.metric(
                        label="Total Productos",
                        value=f"{total_productos:,}",
                        delta="Únicos"
                    )
                
                with col2:
                    total_stock = df['Stock'].sum() if 'Stock' in df.columns else 0
                    st.metric(
                        label="Stock Total",
                        value=f"{total_stock:,.0f}",
                        delta="Unidades"
                    )
                
                with col3:
                    total_valor = df['Valor total'].sum() if 'Valor total' in df.columns else 0
                    st.metric(
                        label="Valor Total Inventario",
                        value=f"${total_valor:,.0f}",
                        delta="COP"
                    )
                
                with col4:
                    if 'Rotación de Inventarios' in df.columns:
                        rotacion_promedio = df['Rotación de Inventarios'].mean()
                        st.metric(
                            label="Rotación Promedio",
                            value=f"{rotacion_promedio:.1f}",
                            delta="Días"
                        )
                
                st.markdown("---")
                
                # ================================
                # TABS PARA ANÁLISIS
                # ================================
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📈 Gráficos", "📋 Datos Detallados", "💾 Guardar Informe", 
                    "📂 Histórico", "ℹ️ Información"
                ])
                
                with tab1:
                    st.markdown("### 📈 Análisis Gráfico")
                    
                    graficos = crear_graficos_analisis(df)
                    
                    # Mostrar gráficos en columnas
                    if 'estado' in graficos or 'cobertura' in graficos:
                        col1, col2 = st.columns(2)
                        with col1:
                            if 'estado' in graficos:
                                st.plotly_chart(graficos['estado'], use_container_width=True)
                        with col2:
                            if 'cobertura' in graficos:
                                st.plotly_chart(graficos['cobertura'], use_container_width=True)
                    
                    if 'top_productos' in graficos:
                        st.plotly_chart(graficos['top_productos'], use_container_width=True)
                    
                    if 'rotacion' in graficos:
                        st.plotly_chart(graficos['rotacion'], use_container_width=True)
                
                with tab2:
                    st.markdown("### 📋 Tabla de Datos")
                    
                    # Filtros adicionales
                    col1, col2 = st.columns(2)
                    with col1:
                        if 'Estado' in df.columns:
                            estados = ['Todos'] + list(df['Estado'].unique())
                            estado_filter = st.selectbox("Filtrar por Estado", estados)
                    with col2:
                        if 'Cobertura Inv' in df.columns:
                            coberturas = ['Todos'] + list(df['Cobertura Inv'].unique())
                            cobertura_filter = st.selectbox("Filtrar por Cobertura", coberturas)
                    
                    # Aplicar filtros
                    df_display = df.copy()
                    if estado_filter != 'Todos':
                        df_display = df_display[df_display['Estado'] == estado_filter]
                    if cobertura_filter != 'Todos':
                        df_display = df_display[df_display['Cobertura Inv'] == cobertura_filter]
                    
                    # Mostrar tabla
                    st.dataframe(df_display, use_container_width=True, height=500)
                    
                    # Descargar datos filtrados
                    csv = df_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar datos (CSV)",
                        data=csv,
                        file_name=f"datos_energia_{mes_actual}_{año_actual}.csv",
                        mime="text/csv"
                    )
                
                with tab3:
                    st.markdown("### 💾 Guardar Informe Mensual")
                    
                    st.info(f"📅 Período: {mes_actual} {año_actual}")
                    st.info(f"👤 Usuario: {usuario}")
                    st.info(f"📊 Total de registros: {len(df)}")
                    
                    if st.button("💾 Guardar en Histórico", type="primary"):
                        with st.spinner('Guardando informe...'):
                            filename = guardar_historico(df, mes_actual, año_actual, usuario)
                            st.success(f"✅ Informe guardado exitosamente: {filename}")
                            
                            # Mostrar archivo para descarga
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    label="📥 Descargar Informe Guardado",
                                    data=f,
                                    file_name=f"informe_{mes_actual}_{año_actual}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                
                with tab4:
                    st.markdown("### 📂 Histórico de Informes")
                    
                    historico = cargar_historico()
                    
                    if historico:
                        # Convertir a DataFrame
                        df_historico = pd.DataFrame(historico)
                        df_historico['fecha'] = pd.to_datetime(df_historico['fecha'])
                        df_historico = df_historico.sort_values('fecha', ascending=False)
                        
                        # Mostrar tabla
                        st.dataframe(
                            df_historico[['mes', 'año', 'fecha', 'usuario', 'registros']],
                            use_container_width=True
                        )
                        
                        # Gráfico de evolución
                        if len(df_historico) > 1:
                            fig_evolucion = px.line(
                                df_historico,
                                x='fecha',
                                y='registros',
                                title='Evolución de Registros Mensuales',
                                markers=True
                            )
                            st.plotly_chart(fig_evolucion, use_container_width=True)
                    else:
                        st.warning("No hay informes guardados en el histórico")
                
                with tab5:
                    st.markdown("### ℹ️ Información del Sistema")
                    
                    st.markdown("""
                    #### 📋 Guía de Uso
                    
                    1. **Cargar Archivo**: Sube el archivo XLSB mensual desde el sidebar
                    2. **Revisar Métricas**: Verifica los indicadores principales
                    3. **Analizar Gráficos**: Explora los diferentes análisis visuales
                    4. **Filtrar Datos**: Usa los filtros para análisis específicos
                    5. **Guardar Informe**: Guarda el informe en el histórico mensual
                    6. **Consultar Histórico**: Revisa informes anteriores
                    
                    #### 🎨 Personalización
                    
                    - **Logo**: Reemplaza la imagen del sidebar con tu logo corporativo
                    - **Colores**: Modifica los colores en la sección de estilos CSS
                    - **Gerencia**: Cambia el filtro de gerencia según necesites
                    
                    #### 📊 Columnas Principales
                    
                    - **Producto**: Código del material
                    - **Descripción**: Nombre del producto
                    - **Stock**: Cantidad en inventario
                    - **Valor total**: Valor monetario del inventario
                    - **Estado**: Estado de consumo
                    - **Cobertura Inv**: Días de cobertura
                    - **Rotación de Inventarios**: Días de rotación
                    
                    #### 🔒 Control de Cambios
                    
                    Cada informe guardado registra:
                    - Fecha y hora de generación
                    - Usuario que lo generó
                    - Período (mes/año)
                    - Número de registros
                    """)
            else:
                st.warning(f"⚠️ No se encontraron datos para la gerencia '{gerencia_filter}'")
            
            # Limpiar archivo temporal
            if os.path.exists(xlsx_path):
                os.remove(xlsx_path)
else:
    # Pantalla de inicio
    st.markdown("""
        <div style='text-align: center; padding: 3rem;'>
            <h2>👋 Bienvenido al Dashboard de Energía</h2>
            <p style='font-size: 1.2rem; color: #6B7280;'>
                Para comenzar, carga un archivo XLSB desde el panel lateral
            </p>
            <br>
            <p>📁 Soporta archivos en formato XLSB</p>
            <p>⚡ Análisis automático de datos de energía</p>
            <p>📊 Gráficos interactivos en tiempo real</p>
            <p>💾 Sistema de histórico mensual</p>
            <p>👤 Control de versiones por usuario</p>
        </div>
    """, unsafe_allow_html=True)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #6B7280; padding: 1rem;'>
        <p>Dashboard Gerencia de Energía v1.0 | Desarrollado con ❤️ usando Streamlit</p>
        <p>© 2026 Tu Empresa - Todos los derechos reservados</p>
    </div>
""", unsafe_allow_html=True)
