"""Identidad aleatoria persistente en el navegador, sin formularios de registro."""
import hashlib
import re

import streamlit as st
import streamlit.components.v2 as components


BROWSER_JS = r"""
export default function({data, setStateValue}) {
    let active = true;
    const storageKey = data.storage_key;
    function readOrCreate() {
        let token = window.localStorage.getItem(storageKey);
        if (token === null) {
            const bytes = new Uint8Array(32);
            window.crypto.getRandomValues(bytes);
            token = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
            window.localStorage.setItem(storageKey, token);
        }
        if (!/^[a-f0-9]{64}$/.test(token)) {
            throw new Error('invalid_identity');
        }
        // No continuar si el navegador no conserva realmente el valor.
        if (window.localStorage.getItem(storageKey) !== token) {
            throw new Error('storage_unavailable');
        }
        return {ready: true, token, error: null};
    }
    async function synchronize() {
        try {
            // Evitar identidades distintas al abrir por primera vez dos pestañas a la vez.
            const identity = window.navigator.locks
                ? await window.navigator.locks.request(storageKey, readOrCreate)
                : readOrCreate();
            if (active) setStateValue('identity', identity);
        } catch (_) {
            if (active) setStateValue('identity', {ready: true, token: null, error: 'storage_unavailable'});
        }
    }
    const onStorage = (event) => {
        if (event.key === storageKey || event.key === null) synchronize();
    };
    window.addEventListener('storage', onStorage);
    synchronize();
    return () => {active = false; window.removeEventListener('storage', onStorage);};
}
"""

_browser_component = components.component("xeco_browser_identity", js=BROWSER_JS)


def browser_identity(project_url):
    # El almacenamiento pertenece al dominio de la app y al proyecto configurado.
    project_hash = hashlib.sha256(project_url.strip().rstrip("/").encode()).hexdigest()[:20]
    result = _browser_component(
        key="xeco_identity_component", height=0,
        data={"storage_key": f"xeco_browser_v1_{project_hash}"},
        on_identity_change=lambda: None,
    )
    identity = result.identity
    if not identity or not identity.get("ready"):
        st.info("Preparando tu historial…")
        st.stop()
    token = identity.get("token")
    if identity.get("error") or not isinstance(token, str) or not re.fullmatch(r"[a-f0-9]{64}", token):
        st.error("El navegador no permite recordar tu historial. Habilita el almacenamiento de este sitio y recarga la página.")
        st.stop()
    return token
