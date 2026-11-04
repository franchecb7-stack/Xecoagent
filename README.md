# Xecoagent

Asistente económico desarrollado con Python, Groq y Streamlit. Consulta datos del Banco Mundial, Fondo Monetario Internacional y un servicio de tipo de cambio.

## Publicar y obtener un enlace

Estos pasos se realizan una sola vez. Los visitantes usarán el navegador; no necesitan instalar Python ni Visual Studio Code.

### 1. Subir a GitHub

1. Descomprime `Xecoagent_para_publicar.zip`.
2. Inicia sesión en https://github.com y crea un repositorio llamado `Xecoagent`.
3. Usa **Add file → Upload files** y sube el contenido de la carpeta `Xecoagent_publicar` a la raíz del repositorio.
4. Confirma que aparezcan estos archivos con sus nombres exactos, sin `(1)` ni `(2)`:

```text
Xecoagent.py
basic_agent_basic_memory_intermediate_tools.py
basic_memory.py
intermediate_tools.py
requirements.txt
README.md
secrets.example.toml
```

Incluye también `.gitignore` y `.env.example` si tu explorador los muestra. No subas `.env`, un archivo `download` que contenga tu clave, `.streamlit/secrets.toml` ni tu entorno virtual. Este ZIP no contiene claves reales.

### 2. Crear la app en Streamlit Community Cloud

1. Entra a https://share.streamlit.io/ e inicia sesión conectando tu cuenta de GitHub.
2. Pulsa **Create app** y elige la opción para una aplicación que ya existe.
3. Selecciona el repositorio `Xecoagent`, la rama donde subiste los archivos (normalmente `main`) y, en **Main file path**, escribe `Xecoagent.py`.
4. Abre **Advanced settings**, selecciona Python **3.12** y pega en **Secrets** lo siguiente, reemplazando el texto entre comillas por tu clave real:

```toml
GROQ_API_KEY = "coloca_aqui_tu_api_key"
```

5. Guarda y pulsa **Deploy**. Espera a que termine la instalación y se abra el chat.
6. Copia la URL real terminada en `.streamlit.app` que asigne Streamlit. Si la app tiene acceso restringido, ajusta sus opciones de compartir para permitir a los destinatarios entrar.

La app se ejecutará en los servidores de Streamlit; tu computadora no tiene que permanecer encendida. La disponibilidad y el uso dependen de los límites de Streamlit, Groq y las fuentes de datos. Todos los visitantes utilizan la clave de Groq configurada por ti; ellos no introducen una clave.

### 3. Probar el enlace

Abre la URL en incógnito o desde otro dispositivo y pregunta: **¿Cuál fue la inflación de Guatemala en 2023?** Comprueba también que una conversación nueva no muestre mensajes de otra sesión. Si hay un error, revisa **Manage app → Logs** y la configuración de Secrets.

## Ejecutar localmente en Windows / Visual Studio Code

Abre Visual Studio Code, selecciona **File → Open Folder** para abrir esta carpeta y después **Terminal → New Terminal**.

La primera vez, ejecuta:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crea un archivo `.env` junto a `Xecoagent.py` con:

```text
GROQ_API_KEY=coloca_aqui_tu_api_key
```

Inicia la app desde la terminal:

```powershell
python -m streamlit run Xecoagent.py
```

Abre http://localhost:8501 si el navegador no se abre automáticamente. Presiona **Ctrl + C** para detenerla.

Para volver a ejecutar después de abrir una terminal nueva:

```powershell
.\env\Scripts\Activate.ps1
python -m streamlit run Xecoagent.py
```

Si PowerShell impide activar el entorno, puedes utilizar directamente:

```powershell
.\env\Scripts\python.exe -m streamlit run Xecoagent.py
```

## Cambios para publicación

- Nombres de módulos normalizados, sin sufijos de descarga.
- Clave leída desde Secrets o `.env` local; indicación en pantalla si falta.
- Historial separado por sesión y contexto del modelo limitado a los últimos 10 mensajes.
- Máximo de ocho rondas de llamadas al modelo por consulta y tiempo de espera para Groq.
- Errores para visitantes sin detalles internos de excepciones.
- Herramientas económicas e interfaz conservadas.

El modelo predeterminado sigue siendo `openai/gpt-oss-120b`. Puede cambiarse mediante la variable de entorno `GROQ_MODEL` o un secreto de nivel superior en Streamlit, usando un modelo disponible en tu cuenta que admita herramientas.

## Documentación oficial

- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management

## Validación

Se verificaron los módulos y el arranque con pruebas de Streamlit sin consumir tu clave. La prueba final en tu cuenta requiere una clave válida y acceso a Groq y a los servicios de datos.
