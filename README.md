# Xecoagent con historial sin registro

Asistente económico con Python, Groq, Streamlit y Supabase. Esta versión guarda conversaciones sin pedir correo ni contraseña.

## Cómo funciona

Al abrir la app, el navegador genera una clave aleatoria y la conserva en el almacenamiento del sitio. Las conversaciones se guardan en Supabase, separadas por esa clave. Al volver desde el mismo navegador, se pueden abrir los chats anteriores desde la barra lateral.

La identidad no se añade al enlace de la aplicación. Compartir la URL permite abrir la app sin compartir tus conversaciones. Otra persona que utilice ese mismo perfil del navegador y dispositivo sí podrá ver el historial de ese perfil.

Si borras los datos del sitio, cambias de navegador, usas otro dispositivo o cierras una sesión de incógnito, no recuperarás ese historial. Las conversaciones ya perdidas antes de instalar esta versión tampoco se pueden reconstruir.

## Activar en tu aplicación publicada

Sigue **[SUPABASE.md](SUPABASE.md)**. Incluye la creación de la tabla, las políticas de acceso, los Secrets y la actualización del repositorio.

No necesitas activar registro por correo, SMTP ni Supabase Auth. No se utilizan usuarios anónimos de Supabase Auth: la separación se realiza mediante una clave de navegador y políticas RLS que comprueban su hash en cada petición.

## Archivos principales

| Archivo | Función |
|---|---|
| `Xecoagent.py` | Interfaz y consultas económicas |
| `browser_identity.py` | Genera y recupera la clave persistente del navegador |
| `history_ui.py` | Lista de chats, nueva conversación, apertura y guardado |
| `supabase_history.py` | Lectura y escritura en Supabase |
| `supabase_setup.sql` | Tabla y reglas de acceso |
| `requirements.txt` | Dependencias |

## Ejecución local en Windows

Desde la terminal de Visual Studio Code, dentro de la carpeta del proyecto:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crea un `.env` con los valores de `.env.example` y ejecuta:

```powershell
python -m streamlit run Xecoagent.py
```

Usa Python 3.12. Si ya tienes el entorno, solo actualiza las dependencias y ejecuta la app. Para detenerla, presiona Ctrl+C. No subas `.env` ni tu entorno virtual a GitHub.

Si no configuras los dos valores de Supabase, la app conserva el modo temporal anterior. El historial permanente requiere completar la configuración.

## Verificación

```powershell
python -m unittest discover -s tests -v
```

Las pruebas incluidas simulan las respuestas HTTP. Se comprobaron también los flujos de interfaz con Streamlit AppTest y la generación/recuperación de la identidad con almacenamiento simulado. No sustituyen una prueba en el navegador real ni la ejecución del SQL en tu proyecto Supabase.
