import streamlit as st
import re
import logging
import pandas as pd

from basic_agent_basic_memory_intermediate_tools import (
    get_client,
    process_response
)


# Configuración de la página
st.set_page_config(
    page_title="Xecoagent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Configuración de credenciales: Secrets en Streamlit, .env en ejecución local.
try:
    api_key = st.secrets.get("GROQ_API_KEY")
except FileNotFoundError:
    api_key = None

try:
    client = get_client(api_key)
except ValueError:
    st.error(
        "Falta configurar la clave de Groq. En Streamlit Community Cloud, "
        "abre Settings → Secrets y agrega GROQ_API_KEY. "
        "Si ejecutas la app en tu computadora, configura el archivo .env."
    )
    st.stop()


# Diseño visual
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(37, 99, 235, 0.15),
                transparent 30%
            ),
            linear-gradient(135deg, #0f172a, #111827);
        color: #f8fafc;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    [data-testid="stSidebar"] * {
        color: #1f2937;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }

    .titulo-principal {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0;
    }

    .subtitulo {
        text-align: center;
        color: #cbd5e1;
        font-size: 17px;
        margin-top: 4px;
        margin-bottom: 28px;
    }

    .tarjeta {
        background: rgba(51, 65, 85, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 15px;
        padding: 18px 10px;
        text-align: center;
        color: #ffffff;
        min-height: 100px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
    }

    .tarjeta-icono {
        font-size: 25px;
        margin-bottom: 7px;
    }

    .tarjeta-texto {
        font-size: 16px;
        font-weight: 650;
    }

    .encabezado-chat {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        border-radius: 16px 16px 0 0;
        padding: 17px 22px;
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-top: 25px;
    }

    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.97);
        border: 1px solid #e5e7eb;
        border-radius: 15px;
        padding: 12px 16px;
        margin-bottom: 12px;
        color: #111827;
    }

    /* Texto dentro de los mensajes */
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] em,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] h4 {
        color: #111827 !important;
    }

    /* Mantener blancos los encabezados de las tablas */
    [data-testid="stChatMessage"] th,
    [data-testid="stChatMessage"] th strong {
        color: #ffffff !important;
    }

    [data-testid="stChatInput"] {
        background: #111827;
    }

    .nombre-lateral {
        font-size: 30px;
        font-weight: 800;
        text-align: center;
        margin-top: 10px;
    }

    .descripcion-lateral {
        color: #6b7280;
        text-align: center;
        font-size: 13px;
        margin-bottom: 22px;
    }

    .herramienta {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 14px;
    }

    .stButton button {
        width: 100%;
        border-radius: 10px;
        min-height: 42px;
    }

    /* Permitir desplazamiento horizontal en tablas grandes */
    [data-testid="stChatMessage"] .stMarkdown {
        overflow-x: auto;
    }

    /* Diseño general de la tabla */
    [data-testid="stChatMessage"] table {
        width: 100%;
        min-width: 900px;
        border-collapse: separate;
        border-spacing: 0;
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 14px;
        margin-bottom: 18px;
        font-size: 14px;
    }

    /* Encabezados */
    [data-testid="stChatMessage"] thead tr {
        background: #2563eb !important;
    }

    [data-testid="stChatMessage"] th {
        background: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700;
        padding: 13px 10px;
        text-align: center;
        white-space: normal;
        border-right: 1px solid #60a5fa;
        border-bottom: 1px solid #1d4ed8;
    }

    /* Celdas */
    [data-testid="stChatMessage"] td {
        background: #ffffff !important;
        color: #111827 !important;
        padding: 12px 10px;
        text-align: center;
        white-space: nowrap;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }

    /* Filas alternadas */
    [data-testid="stChatMessage"] tbody tr:nth-child(even) td {
        background: #f1f5f9 !important;
    }

    /* Color al pasar el cursor */
    [data-testid="stChatMessage"] tbody tr:hover td {
        background: #dbeafe !important;
    }

    /* Eliminar bordes sobrantes */
    [data-testid="stChatMessage"] th:last-child,
    [data-testid="stChatMessage"] td:last-child {
        border-right: none;
    }

    [data-testid="stChatMessage"] tbody tr:last-child td {
        border-bottom: none;
    }

    /* Asegurar que todo el texto sea visible */
    [data-testid="stChatMessage"] table,
    [data-testid="stChatMessage"] table * {
        visibility: visible !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Convertir un texto numérico a un valor que pueda graficarse
def convertir_a_numero(valor):
    texto = str(valor).strip()

    if texto.upper() in ("N/D", "ND", "N/A", ""):
        return None

    texto = re.sub(
        r"(?i)USD|MM|millones|mil millones|habitantes|del PIB|%",
        "",
        texto
    )

    texto = texto.replace(" ", "")
    texto = re.sub(r"[^0-9,.-]", "", texto)

    if not texto:
        return None

    # Reconocer formato español e inglés
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


# Extraer la primera tabla Markdown de una respuesta
def extraer_tabla_markdown(texto):
    lineas = [
        linea.strip()
        for linea in texto.splitlines()
        if linea.strip()
    ]

    for posicion in range(len(lineas) - 1):
        encabezado = lineas[posicion]
        separador = lineas[posicion + 1]

        if (
            "|" in encabezado
            and "|" in separador
            and "---" in separador
        ):
            columnas = [
                celda.strip()
                for celda in encabezado.strip("|").split("|")
            ]

            filas = []
            indice = posicion + 2

            while indice < len(lineas) and "|" in lineas[indice]:
                fila = [
                    celda.strip()
                    for celda in lineas[indice].strip("|").split("|")
                ]

                if len(fila) == len(columnas):
                    filas.append(fila)

                indice += 1

            if filas:
                return pd.DataFrame(filas, columns=columnas)

    return None


# Convertir la tabla encontrada en gráficas de líneas
def mostrar_graficas(texto):
    tabla = extraer_tabla_markdown(texto)

    if tabla is None or tabla.empty or len(tabla.columns) < 2:
        st.info(
            "No fue posible encontrar datos tabulares para graficar."
        )
        return

    columna_anio = tabla.columns[0]
    tabla[columna_anio] = tabla[columna_anio].apply(
        convertir_a_numero
    )

    for columna in tabla.columns[1:]:
        valores = tabla[columna].apply(convertir_a_numero)

        datos_grafica = pd.DataFrame({
            "Año": tabla[columna_anio],
            columna: valores
        }).dropna()

        if datos_grafica.empty:
            continue

        datos_grafica["Año"] = (
            datos_grafica["Año"].astype(int)
        )

        datos_grafica = datos_grafica.set_index("Año")

        st.markdown(f"#### Gráfica: {columna}")
        st.line_chart(datos_grafica)

# Mensaje inicial
def mensajes_iniciales():
    return [
        {
            "role": "assistant",
            "content": (
                "Hola, soy Xecoagent, tu asistente de análisis "
                "económico. Puedo consultar inflación, PIB per cápita, "
                "crecimiento económico, deuda pública, desempleo y "
                "tipos de cambio. ¿Qué deseas analizar?"
            )
        }
    ]


# Memoria del chat
if "messages" not in st.session_state:
    st.session_state["messages"] = mensajes_iniciales()


# Barra lateral
with st.sidebar:
    st.markdown(
        '<div class="nombre-lateral">📊 Xecoagent</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="descripcion-lateral">'
        'Asistente inteligente de análisis económico'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("🗑️ Limpiar conversación"):
        st.session_state["messages"] = mensajes_iniciales()
        st.rerun()

    st.markdown("### Herramientas disponibles")

    herramientas = [
        "💱 Tipo de cambio",
        "📈 Inflación",
        "💰 PIB per cápita",
        "📊 Crecimiento económico",
        "🏛️ Deuda pública",
        "👥 Desempleo"
    ]

    for herramienta in herramientas:
        st.markdown(
            f'<div class="herramienta">{herramienta}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption(
        "Fuentes: Banco Mundial, Fondo Monetario Internacional "
        "y servicio de tipo de cambio."
    )


# Título principal
st.markdown(
    '<div class="titulo-principal">📊 Xecoagent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Asistente inteligente de análisis macroeconómico'
    '</div>',
    unsafe_allow_html=True
)


# Tarjetas superiores
col1, col2, col3, col4, col5, col6 = st.columns(6)

tarjetas = [
    (col1, "💱", "Tipo de cambio"),
    (col2, "📈", "Inflación"),
    (col3, "💰", "PIB per cápita"),
    (col4, "📊", "Crecimiento"),
    (col5, "🏛️", "Deuda pública"),
    (col6, "👥", "Desempleo")
]

for columna, icono, nombre in tarjetas:
    with columna:
        st.markdown(
            f"""
            <div class="tarjeta">
                <div class="tarjeta-icono">{icono}</div>
                <div class="tarjeta-texto">{nombre}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# Encabezado del chat
st.markdown(
    '<div class="encabezado-chat">🤖 Agente económico</div>',
    unsafe_allow_html=True
)


# Mostrar historial
for mensaje in st.session_state["messages"]:
    avatar = "🤖" if mensaje["role"] == "assistant" else "👤"

    with st.chat_message(
        mensaje["role"],
        avatar=avatar
    ):
        st.markdown(mensaje["content"])

        # Mostrar la gráfica solo si fue solicitada
        if (
            mensaje["role"] == "assistant"
            and mensaje.get("mostrar_grafica", False)
        ):
            mostrar_graficas(mensaje["content"])


# Entrada del usuario
pregunta = st.chat_input(
    "Escribe una pregunta para Xecoagent..."
)

if pregunta:
    texto_pregunta = pregunta.lower()

    palabras_grafica = (
        "gráfica",
        "grafica",
        "gráfico",
        "grafico",
        "chart"
    )

    solicitar_grafica = any(
        palabra in texto_pregunta
        for palabra in palabras_grafica
    )

    # Enviar al modelo únicamente role y content
    memoria_anterior = [
        {
            "role": mensaje["role"],
            "content": mensaje["content"]
        }
        for mensaje in st.session_state["messages"]
    ]

    st.session_state["messages"].append(
        {
            "role": "user",
            "content": pregunta
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.write(pregunta)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Consultando indicadores económicos..."):
            try:
                respuesta = process_response(
                    client,
                    memoria_anterior,
                    pregunta
                )
            except Exception as error:
                logging.getLogger(__name__).warning(
                    "Consulta fallida (%s)", type(error).__name__
                )
                respuesta = (
                    "No fue posible procesar la consulta. "
                    "Intenta nuevamente en unos momentos. Si el problema continúa, "
                    "el administrador debe revisar la clave, el modelo y los límites de Groq."
                )

        st.markdown(respuesta)

        # Crear la gráfica solamente cuando el usuario la solicite
        if solicitar_grafica:
            mostrar_graficas(respuesta)

    st.session_state["messages"].append(
        {
            "role": "assistant",
            "content": respuesta,
            "mostrar_grafica": solicitar_grafica
        }
    )