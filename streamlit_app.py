import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

# Fonction de génération
def generate_system():
    order = random.choice([1, 2])
    t = np.linspace(0, 10, 500)

    if order == 1:
        K = round(random.uniform(0.5, 5.0), 2)
        tau = round(random.uniform(0.5, 3.0), 2)
        y = K * (1 - np.exp(-t / tau))
        params = {'K': K, 'tau': tau}
    else:
        K = round(random.uniform(0.5, 5.0), 2)
        omega_0 = round(random.uniform(1, 5.0), 2)
        xi = round(random.uniform(0.3, 1,8), 2)
        if xi < 1:
            y = K * (1 - (1 / np.sqrt(1 - xi**2)) * np.exp(-xi * omega_0 * t) *
                     np.sin(omega_0 * np.sqrt(1 - xi**2) * t + np.arccos(xi)))
        else:
            y = K * (1 - np.exp(-xi * omega_0 * t) *
                     np.cosh(omega_0 * np.sqrt(xi**2 - 1) * t))
        params = {'K': K, 'omega_0': omega_0, 'xi': xi}
    return order, t, y, params

# Initialisation / génération
if 'confirmed_refresh' not in st.session_state:
    st.session_state.confirmed_refresh = False
if 'order' not in st.session_state or st.session_state.confirmed_refresh:
    st.session_state.order, st.session_state.t, st.session_state.y, st.session_state.params = generate_system()
    st.session_state.confirmed_refresh = False

# Créer les onglets
tabs = st.tabs(["🔍 Identification", "📊 Comparaison (si second ordre)"])

# ------------------- ONGLET 1 : Identification -------------------
with tabs[0]:
    st.title("🔎 Identification d'un système (réponse indicielle)")

    # Sliders pour aides graphiques
    st.sidebar.markdown("### ➕ Aides visuelles")

    # Droites horizontales
    show_h1 = st.sidebar.checkbox("Afficher une première droite horizontale", value=False)
    h1_val = st.sidebar.slider("Valeur Y1 (1ère ligne)", 0.0, 3.0, 1.0, 0.1) if show_h1 else None

    show_h2 = st.sidebar.checkbox("Afficher une deuxième droite horizontale", value=False)
    h2_val = st.sidebar.slider("Valeur Y2 (2e ligne)", 0.0, 3.0, 2.0, 0.1) if show_h2 else None

    # Droite verticale
    show_vline = st.sidebar.checkbox("Afficher une droite verticale", value=False)
    vline_val = st.sidebar.slider("Temps (droite verticale)", 0.0, 10.0, 1.0, 0.1) if show_vline else None

    fig, ax = plt.subplots()
    ax.plot(st.session_state.t, st.session_state.y, label='Réponse mesurée')

    if show_h1:
        ax.axhline(h1_val, color='tab:red', linestyle='--', label=f'y₁ = {h1_val}')
    if show_h2:
        ax.axhline(h2_val, color='tab:orange', linestyle='--', label=f'y₂ = {h2_val}')
    if show_vline:
        ax.axvline(vline_val, color='tab:green', linestyle='--', label=f't = {vline_val}')

    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Réponse indicielle aléatoire")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    st.subheader("🎯 Estime les paramètres du système")
    order_guess = st.radio("Quel est l'ordre du système affiché ?", ["Premier ordre", "Second ordre"])
    K = st.number_input("K", min_value=0.0, step=0.1)
    if order_guess == "Premier ordre":
        tau = st.number_input("τ", min_value=0.0, step=0.1)
    else:
        omega = st.number_input("ω₀", min_value=0.0, step=0.1)
        xi = st.number_input("ξ", min_value=0.0, step=0.05)

    if st.button("✅ Valider"):
        correct = False
        real = st.session_state.params
        if order_guess == "Premier ordre" and st.session_state.order == 1:
            if abs(K - real['K']) < 0.2 and abs(tau - real['tau']) < 0.2:
                correct = True
        elif order_guess == "Second ordre" and st.session_state.order == 2:
            if (abs(K - real['K']) < 0.2 and
                abs(omega - real['omega_0']) < 0.2 and
                abs(xi - real['xi']) < 0.2):
                correct = True
        if correct:
            st.success("Bonne réponse 🎉")
        else:
            st.error("Incorrect. Essaie encore.")

    if st.button("🔁 Générer un nouveau système"):
        st.session_state.ready_to_refresh = True

    if st.session_state.get("ready_to_refresh", False):
        if st.button("🟢 Oui, je veux vraiment un autre graphe"):
            st.session_state.confirmed_refresh = True
            st.session_state.ready_to_refresh = False
            st.experimental_rerun = lambda: None
            st.stop()

# ------------------- ONGLET 2 : Comparaison -------------------
with tabs[1]:
    st.title("📊 Comparaison second ordre vs 1er ordre")
    if st.session_state.order == 2:
        K2 = st.session_state.params['K']
        t = st.session_state.t
        y2 = st.session_state.y

        tau_approx = st.slider("τ (du 1er ordre à comparer)", 0.1, 5.0, 1.0, 0.1)
        y1 = K2 * (1 - np.exp(-t / tau_approx))

        fig2, ax2 = plt.subplots()
        ax2.plot(t, y2, label="Réponse second ordre (réel)")
        ax2.plot(t, y1, '--', label="Réponse premier ordre (approché)")
        ax2.set_xlabel("Temps (s)")
        ax2.set_ylabel("Amplitude")
        ax2.set_title("Comparaison visuelle")
        ax2.grid(True)
        ax2.legend()
        st.pyplot(fig2)
    else:
        st.info("👉 Ce système est du premier ordre : il n'y a rien à comparer ici.")
