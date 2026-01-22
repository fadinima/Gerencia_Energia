import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import json

# ===================================
# CONFIGURACIÓN
# ===================================
st.set_page_config(
    page_title="Coberturas de Inventario - Gerencia de Energía",
    page_icon="⚡",
    layout="wide"
)

# ===================================
# ESTILOS CSS
# ===================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; }
.main { background: #F5F7FA; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

/* Header */
.header { background: linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%); padding: 1.5rem 2rem; border-radius: 12px; 
         margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,188,212,0.2); display: flex; justify-content: space-between; align-items: center; }
.header h1 { color: white; margin: 0; font-size: 1.75rem; font-weight: 700; }
.header p { color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.95rem; }
.logo-badge { background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 8px; color: white; font-weight: 600; }

/* KPI Cards */
.kpi-card { background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #E8EBED; 
           box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }
.kpi-card:hover { box-shadow: 0 4px 16px rgba(0,188,212,0.15); border-color: #00BCD4; }
.kpi-label { font-size: 0.8rem; font-weight: 600; color: #7F8C8D; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
.kpi-value { font-size: 2.25rem; font-weight: 700; color: #2C3E50; line-height: 1.2; }
.kpi-delta { font-size: 0.85rem; color: #7F8C8D; margin-top: 0.5rem; }

/* Section Card */
.section-card { background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #E8EBED; 
               margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section-title { font-size: 1.1rem; font-weight: 600; color: #2C3E50; margin-bottom: 1rem; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0; background: white; border-bottom: 2px solid #E8EBED; padding: 0 1rem; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #7F8C8D; font-weight: 500; padding: 1rem 1.5rem; 
                                border-bottom: 3px solid transparent; margin-bottom: -2px; }
.stTabs [data-baseweb="tab"]:hover { color: #00BCD4; background: rgba(0,188,212,0.05); }
.stTabs [aria-selected="true"] { color: #00BCD4 !important; border-bottom-color: #00BCD4 !important; font-weight: 600 !important; }

/* Dataframe */
.dataframe { font-size: 0.85rem !important; border: 1px solid #E8EBED !important; }
.dataframe thead th { background: #F8FAFB !important; color: #2C3E50 !important; font-weight: 600 !important; 
                      text-transform: uppercase; font-size: 0.75rem !important; padding: 0.75rem !important; }
.dataframe tbody tr:hover { background: rgba(0,188,212,0.05) !important; }

/* Buttons */
.stButton>button { background: linear-gradient(135deg, #00BCD4, #00ACC1); color: white !important; border: none; 
                  border-radius: 8px; padding: 0.65rem 1.5rem; font-weight: 600; box-shadow: 0 2px 8px rgba(0,188,212,0.25); }
.stButton>button:hover { box-shadow: 0 4px 16px rgba(0,188,212,0.35); transform: translateY(-1px); }

/* File uploader */
[data-testid="stFileUploader"] { background: white; border: 2px dashed #DDE6ED; border-radius: 12px; padding: 1.5rem; }

/* Inputs */
input, select { background: white !important; border: 1.5px solid #DDE6ED !important; border-radius: 8px !important; padding: 0.65rem !important; }
input:focus, select:focus { border-color: #00BCD4 !important; box-shadow: 0 0 0 3px rgba(0,188,212,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ===================================
# FUNCIONES
# ===================================

def formatear_valor(valor):
    """Formatea valores grandes"""
    if valor >= 1e9:
        return f"${valor/1e9:.1f}B"
    elif valor >= 1e6:
        return f"${valor/1e6:.1f}M"
    elif valor >= 1e3:
        return f"${valor/1e3:.1f}K"
    else:
        return f"${valor:.0f}"

def crear_grafico_dona(datos, titulo):
    """Crea gráfico de dona profesional"""
    labels = list(datos.keys())
    values = list(datos.values())
    
    colores = ['#00BCD4', '#00ACC1', '#26C6DA', '#4DD0E1', '#80DEEA']
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker=dict(colors=colores, line=dict(color='white', width=2)),
        textposition='outside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.0f}<br>%{percent}<extra></extra>'
    ))
    
    total = sum(values)
    fig.add_annotation(
        text=f"<b>Total</b><br>{formatear_valor(total)}",
        x=0.5, y=0.5,
        font=dict(size=14, color='#2C3E50'),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15, color='#2C3E50', weight=600), x=0.5, xanchor='center'),
        height=420,
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, x=1.05, font=dict(size=10)),
        margin=dict(l=20, r=150, t=60, b=20)
    )
    
    return fig

def cargar_datos_xlsx(file):
    """Carga archivo XLSX"""
    try:
        df = pd.read_excel(file, sheet_name='informe')
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
        return None

def guardar_historico(df, mes, año, usuario):
    """Guarda informe"""
    os.makedirs("historico_informes", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"historico_informes/informe_{mes}_{año}_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
        
        metadata = pd.DataFrame({
            'Mes': [mes], 'Año': [año],
            'Fecha': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Usuario': [usuario], 'Registros': [len(df)]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
    
    return filename

# ===================================
# INTERFAZ
# ===================================

# Header
st.markdown("""
<div class="header">
    <div>
        <h1>📊 Coberturas de Inventario - Cierre de Mes</h1>
        <p>Gerencia de Energía • Sistema de Análisis de Inventarios</p>
    </div>
    <div class="logo-badge">⚡ ENERGÍA</div>
</div>
""", unsafe_allow_html=True)

# Barra de configuración
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📁 Cargar archivo XLSX (convierte tu XLSB a XLSX en Excel primero)",
        type=['xlsx', 'xls'],
        help="Abre tu XLSB en Excel → Guardar como → XLSX"
    )

with col2:
    mes = st.selectbox("Mes", ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                                "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"], index=10)

with col3:
    año = st.number_input("Año", 2020, 2030, 2024)

with col4:
    usuario = st.text_input("Usuario", "Admin")

st.markdown("<br>", unsafe_allow_html=True)

# ===================================
# PROCESAMIENTO
# ===================================

if uploaded_file:
    with st.spinner('⚡ Procesando...'):
        df = cargar_datos_xlsx(uploaded_file)
        
        if df is not None and len(df) > 0:
            st.success(f"✅ {len(df):,} registros cargados • {mes} {año}")
            
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            referencias = df['Producto'].nunique()
            stock = df['Stock'].sum()
            valor = df['Valor total'].sum()
            rotacion = df['Rotación de Inventarios'].mean() if 'Rotación de Inventarios' in df.columns else 0
            
            with col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">🎯 REFERENCIAS</div>
                    <div class="kpi-value">{referencias:,}</div>
                    <div class="kpi-delta">SKUs únicos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">📦 STOCK TOTAL</div>
                    <div class="kpi-value">{stock:,.0f}</div>
                    <div class="kpi-delta">unidades</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">💰 VALOR INVENTARIO</div>
                    <div class="kpi-value">{formatear_valor(valor)}</div>
                    <div class="kpi-delta">${valor:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">🔄 ROTACIÓN MEDIA</div>
                    <div class="kpi-value">{rotacion:.0f}</div>
                    <div class="kpi-delta">días promedio</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tabs
            tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Datos", "💾 Guardar"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'Estado' in df.columns:
                        estados = df.groupby('Estado')['Valor total'].sum().to_dict()
                        fig1 = crear_grafico_dona(estados, '💼 Valor por Estado de Consumo')
                        st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    if 'Cobertura Inv' in df.columns:
                        coberturas = df.groupby('Cobertura Inv')['Valor total'].sum().to_dict()
                        fig2 = crear_grafico_dona(coberturas, '📊 Distribución por Cobertura')
                        st.plotly_chart(fig2, use_container_width=True)
                
                st.markdown("### 🏆 Top 10 Productos por Valor")
                top10 = df.nlargest(10, 'Valor total')[['Producto','Descripción','Stock','Valor total','Estado']]
                st.dataframe(top10, use_container_width=True, height=400)
            
            with tab2:
                st.markdown("### 🔍 Filtros")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    estados_list = ['Todos'] + sorted(df['Estado'].unique().tolist())
                    estado_sel = st.selectbox("Estado", estados_list)
                with col2:
                    coberturas_list = ['Todos'] + sorted(df['Cobertura Inv'].unique().tolist())
                    cobertura_sel = st.selectbox("Cobertura", coberturas_list)
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
                
                cols = ['Producto','Descripción','Stock','Valor total','Estado','Cobertura Inv']
                st.dataframe(df_filtrado[cols], use_container_width=True, height=500)
                
                csv = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exportar CSV", csv, f"inventario_{mes}_{año}.csv", "text/csv")
            
            with tab3:
                st.markdown("### 💾 Guardar Informe")
                
                col1, col2 = st.columns([2,1])
                
                with col1:
                    st.info(f"📅 {mes} {año}")
                    st.info(f"👤 {usuario}")
                    st.info(f"📊 {len(df):,} registros")
                
                with col2:
                    if st.button("💾 GUARDAR", use_container_width=True):
                        filename = guardar_historico(df, mes, año, usuario)
                        st.success("✅ Guardado")
                        
                        with open(filename, 'rb') as f:
                            st.download_button("📥 Descargar", f, f"informe_{mes}_{año}.xlsx",
                                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.markdown("""
    <div style='text-align:center; padding:4rem; background:white; border-radius:12px; border:2px dashed #DDE6ED;'>
        <div style='font-size:4rem; margin-bottom:1rem;'>📊</div>
        <h2 style='color:#2C3E50; margin-bottom:1rem;'>Panel de Control de Inventarios</h2>
        <p style='color:#7F8C8D; font-size:1.1rem;'>Carga tu archivo XLSX para comenzar</p>
        <p style='color:#E74C3C; margin-top:1rem;'>⚠️ Convierte tu XLSB a XLSX en Excel primero</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; padding:1rem; background:white; border-radius:8px;'>
    <p style='color:#7F8C8D; font-size:0.85rem; margin:0;'>Dashboard Gerencia de Energía v5.0 Final • Sistema Enterprise</p>
</div>
""", unsafe_allow_html=True)
