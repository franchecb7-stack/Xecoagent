"""Historial de Xecoagent sin registro, asociado al navegador."""
import os
from uuid import uuid4

import streamlit as st

from browser_identity import browser_identity
from supabase_history import SupabaseHistory, HistoryError, HistoryConflict


def setting(name):
    try:
        return st.secrets.get(name) or os.environ.get(name, "")
    except FileNotFoundError:
        return os.environ.get(name, "")


def prepare_history(initial_messages):
    url, key = setting("SUPABASE_URL"), setting("SUPABASE_PUBLISHABLE_KEY")
    if not url and not key:
        return None
    if not url or not key:
        st.error("Para activar el historial, configura SUPABASE_URL y SUPABASE_PUBLISHABLE_KEY en Secrets.")
        st.stop()
    token = browser_identity(url)
    try:
        history = SupabaseHistory(url, key, token)
    except HistoryError as error:
        st.error(str(error))
        st.stop()
    previous = st.session_state.get("xeco_browser_digest")
    if previous != history.owner_hash:
        if previous and st.session_state.get("xeco_pending_save"):
            st.warning("Cambió la identificación de este navegador y hay mensajes sin guardar. Descarga una copia antes de continuar.")
            st.download_button("Descargar mensajes sin guardar", "\n\n".join(
                f"{m['role']}: {m['content']}" for m in st.session_state["messages"]
            ), file_name="conversacion_sin_guardar.txt")
            if not st.button("Continuar con el navegador actual (descarta cambios locales)"):
                st.stop()
        reset_chat(initial_messages)
        st.session_state.pop("xeco_history_picker", None)
        st.session_state["xeco_browser_digest"] = history.owner_hash
    return history


def reset_chat(initial_messages):
    st.session_state["messages"] = initial_messages()
    st.session_state["xeco_conversation_id"] = None
    st.session_state["xeco_version"] = 0
    st.session_state["xeco_pending_save"] = False
    st.session_state["xeco_conflict"] = False


def load_chat(history, conversation_id, initial_messages):
    conversation = history.load(conversation_id)
    st.session_state["messages"] = conversation["messages"] or initial_messages()
    st.session_state["xeco_conversation_id"] = conversation["id"]
    st.session_state["xeco_version"] = conversation["version"]
    st.session_state["xeco_pending_save"] = False
    st.session_state["xeco_conflict"] = False


def save_chat(history):
    if not st.session_state.get("xeco_conversation_id"):
        st.session_state["xeco_conversation_id"] = str(uuid4())
    st.session_state["xeco_pending_save"] = True
    try:
        version = history.save(
            st.session_state["xeco_conversation_id"],
            st.session_state.get("xeco_version", 0),
            st.session_state["messages"],
        )
    except HistoryConflict as error:
        st.session_state["xeco_conflict"] = True
        st.error(str(error))
    except HistoryError as error:
        st.error(str(error) + " Tu conversación sigue visible, pero estos cambios aún no están guardados.")
    else:
        st.session_state["xeco_version"] = version
        st.session_state["xeco_pending_save"] = False
        st.session_state["xeco_conflict"] = False


def history_sidebar(history, initial_messages):
    if history is None:
        st.caption("Historial temporal. Configura Supabase para recuperarlo en futuras visitas.")
        if st.button("🗑️ Limpiar conversación"):
            reset_chat(initial_messages)
            st.rerun()
        return

    st.caption("Historial de este navegador · sin registro")
    pending = st.session_state.get("xeco_pending_save", False)
    conflict = st.session_state.get("xeco_conflict", False)
    if pending:
        st.warning("Hay cambios sin guardar. Reintenta antes de cerrar la página.")
        st.download_button("Descargar copia de los cambios locales", "\n\n".join(
            f"{m['role']}: {m['content']}" for m in st.session_state["messages"]
        ), file_name="conversacion_sin_guardar.txt")
        if conflict:
            if st.button("Recuperar versión guardada (descarta cambios locales)"):
                try:
                    load_chat(history, st.session_state["xeco_conversation_id"], initial_messages)
                except HistoryError as error:
                    st.error(str(error))
                else:
                    st.rerun()
        elif st.button("Reintentar guardado"):
            save_chat(history)
            if not st.session_state["xeco_pending_save"]:
                st.rerun()
    if st.button("➕ Nueva conversación", disabled=pending):
        reset_chat(initial_messages)
        st.rerun()

    st.markdown("### Conversaciones anteriores")
    try:
        conversations = history.list_conversations()
    except HistoryError as error:
        st.error(str(error))
    else:
        if not conversations:
            st.caption("Tu primera consulta iniciará una conversación guardada.")
        ids = [row["id"] for row in conversations]
        labels = {row["id"]: row["title"] for row in conversations}
        selected = st.selectbox("Selecciona una conversación", ids, index=None,
                                format_func=lambda value: labels[value], placeholder="Busca tu conversación",
                                disabled=pending, key="xeco_history_picker") if ids else None
        if st.button("Abrir conversación", disabled=pending or selected is None):
            try:
                load_chat(history, selected, initial_messages)
            except HistoryError as error:
                st.error(str(error))
            else:
                st.rerun()
    st.caption("Nueva conversación conserva las anteriores. El historial se recupera en este mismo navegador; borrar los datos del sitio elimina el acceso.")
