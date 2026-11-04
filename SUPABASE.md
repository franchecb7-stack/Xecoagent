# Activar el historial sin registro

## 1. Crear un proyecto de Supabase

1. Entra a https://supabase.com/dashboard y crea un proyecto para Xecoagent.
2. Espera a que esté disponible.
3. Desde **Connect** o la configuración de **Data API / API Keys**, copia **Project URL** y **Publishable key**. También se admite la antigua clave `anon`.

La contraseña de la base de datos no se utiliza en la aplicación. No uses una clave `service_role` ni `sb_secret_...`.

## 2. Ejecutar el SQL de esta versión

1. Abre **SQL Editor → New query**.
2. Copia todo el contenido del archivo `supabase_setup.sql` de este ZIP.
3. Pégalo y pulsa **Run**.
4. Comprueba que en Table Editor aparezca `xeco_browser_conversations`.

Debes ejecutar este SQL aunque ya hayas instalado la versión anterior con correo. Esta versión usa una tabla diferente y no migra los chats de las cuentas anteriores.

No hay que activar registro por correo, inicio de sesión anónimo de Supabase Auth ni configurar SMTP.

Las políticas RLS comparan el hash de una credencial aleatoria del navegador con `owner_hash`. Sin una credencial válida no se permite leer ni escribir conversaciones. Mantén RLS activado. La aplicación envía la credencial en un encabezado HTTPS, no en la URL; no debes publicarla ni registrarla en logs.

El administrador del proyecto puede acceder a los mensajes desde Supabase. No se trata de cifrado de extremo a extremo.

## 3. Actualizar GitHub

1. Descomprime `Xecoagent_sin_registro_Supabase.zip`.
2. En tu repositorio **franchecb7-stack/Xecoagent**, pulsa **Add file → Upload files**.
3. Sube los archivos dentro de `Xecoagent_sin_registro` directamente a la raíz del repositorio, reemplazando los anteriores. No subas el ZIP como un único archivo.
4. Pulsa **Commit changes**.

Confirma que `Xecoagent.py`, `browser_identity.py`, `history_ui.py`, `supabase_history.py`, las herramientas del agente y `requirements.txt` estén juntos en la raíz. Streamlit necesita actualizar las dependencias porque el identificador utiliza componentes nativos de Streamlit 1.51 o posterior.

## 4. Configurar Streamlit

En tu app publicada, abre **Manage app → Settings → Secrets**. Conserva tu clave vigente de Groq y añade las dos de Supabase:

```toml
GROQ_API_KEY = "tu_clave_vigente_de_groq"
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_tu_clave"
```

Usa comillas y valores de nivel superior, sin encabezados entre corchetes. Guarda. Espera a que la app se actualice o reiníciala desde Manage app. Conserva Python 3.12 y el archivo principal `Xecoagent.py`. La dirección pública de tu aplicación sigue siendo la misma.

Si ya configuraste esos Secrets, conserva sus valores. Para uso local, configura los tres valores en `.env` siguiendo `.env.example`.

## Probar el resultado

1. Abre la aplicación en una ventana normal y haz una pregunta.
2. Espera la respuesta: el guardado se realiza al completar cada respuesta.
3. Pulsa **Nueva conversación** y abre el chat anterior desde la lista lateral.
4. Cierra la pestaña y vuelve a abrir la misma URL en el mismo navegador y perfil. Los chats deben aparecer en la lista. No debe aparecer ningún formulario de registro o acceso.
5. Abre la URL en incógnito o en otro navegador. No debe mostrar las conversaciones de la ventana normal.
6. Comparte solo la URL normal de la app y comprueba que el destinatario puede usarla con su propio historial.

El historial completo se guarda en la base de datos; el modelo sigue recibiendo los últimos 10 mensajes como contexto.

## Si falla el guardado

La aplicación conserva los cambios en la sesión y muestra **Reintentar guardado** y una opción para descargar una copia. No cierres la página mientras haya cambios pendientes. Si dos pestañas modifican a la vez el mismo chat, se detecta el conflicto para evitar sobrescribir mensajes de manera silenciosa.

Si el navegador bloquea el almacenamiento del sitio, aparece una indicación para habilitarlo. No se crea una identidad temporal que pueda perderse sin advertencia.

El identificador depende del dominio de la aplicación. Cambiar el subdominio de Streamlit o el proyecto de Supabase inicia un historial diferente. En un equipo compartido, todas las personas que usen el mismo perfil del navegador comparten ese historial.

## Verificación y límites

Se ejecutaron pruebas unitarias HTTP, pruebas de la interfaz con almacenamiento simulado y pruebas del código JavaScript de identidad. Queda pendiente comprobar el flujo completo en tu app real, ejecutar el SQL y verificar allí RLS con dos navegadores diferentes.

El archivo opcional `tests/verify_rls.sql` permite comprobar las reglas dentro de Supabase con filas de prueba que se revierten al finalizar. Ejecútalo después de `supabase_setup.sql`; no reemplaza la prueba desde dos navegadores.

La disponibilidad y el almacenamiento dependen de tus límites de Streamlit, Supabase y Groq. Esta versión no incluye eliminación de chats ni transferencia del historial entre dispositivos.

## Referencias técnicas

- Streamlit Components v2: https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component
- RLS: https://supabase.com/docs/guides/database/postgres/row-level-security
- Encabezados disponibles para políticas: https://docs.postgrest.org/en/stable/references/transactions.html
