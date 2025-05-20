import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

# --- FONCTION POUR GÉNÉRER UN SYSTÈME ---
def generate_system():
    order = random.choice([1, 2])
    t = np.linspace(0, 10, 500)

    if order == 1:
        K = round(random.uniform(0.5, 2.0), 2)
        tau = round(random.uniform(0.5, 3.0), 2)
        y = K * (1 - np.exp(-t / tau))
        params = {'K': K, 'tau': tau}
    else:
        K = round(random.uniform(0.5, 2.0), 2)
        omega_0 = round(random.uniform(1.0, 3.0), 2)
        xi = round(random.uniform(0.05, 1.2), 2)
        if xi < 1:
            y = K * (1 - (1 / np.sqrt(1 - xi**2)) * np.exp(-xi * omega_0 * t) *
                     np.sin(omega_0 * np.sqrt(1 - xi**2) * t + np.arccos(xi)))
        else:
            y = K * (1 - np.exp(-xi * omega_0 * t) *
                     np.cosh(omega_0 * np.sqrt(xi**2 - 1) * t))
        params = {'K': K, 'omega_0': omega_0, 'xi': xi}
    return order, t, y, params

# --- INITIALISATION CONTROLEE ---
if 'initialized' not in st.session_state:
    st.session_state.order, st.session_state.t, st.session_state.y, st.session_state.params = generate_system()
    st.session_state.initialized = True

# --- TITRE ---
st.title("🔎 Identification d'un système (réponse indicielle)")

# --- AFFICHAGE GRAPHIQUE ---
fig, ax = plt.subplots()
ax.plot(st.session_state.t, st.session_state.y)
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Amplitude")
ax.set_title("Réponse indicielle aléatoire")
ax.grid(True)
st.pyplot(fig)

# --- FORMULAIRE UTILISATEUR ---
st.subheader("🎯 Estime les paramètres du système")
order_guess = st.radio("Quel est l'ordre du système affiché ?", ["Premier ordre", "Second ordre"])
K = st.number_input("K", min_value=0.0, step=0.1)

if order_guess == "Premier ordre":
    tau = st.number_input("tau", min_value=0.0, step=0.1)
else:
    omega = st.number_input("ω₀", min_value=0.0, step=0.1)
    xi = st.number_input("ξ", min_value=0.0, step=0.05)

# --- VALIDATION ---
if st.button("✅ Valider"):
    correct = False
    real = st.session_state.params
    if order_guess == "Premier ordre" and st.session_state.order == 1:
        if abs(K - real['K']) < 0.1 and abs(tau - real['tau']) < 0.1:
            correct = True
    elif order_guess == "Second ordre" and st.session_state.order == 2:
        if (abs(K - real['K']) < 0.1 and
            abs(omega - real['omega_0']) < 0.1 and
            abs(xi - real['xi']) < 0.1):
            correct = True

    if correct:
        st.success("Bonne réponse 🎉")
    else:
        st.error("Incorrect. Essaie encore.")

# --- REGENERATION GRAPHIQUE ---
if st.button("🔁 Générer un nouveau système"):
    st.session_state.order, st.session_state.t, st.session_state.y, st.session_state.params = generate_system()
