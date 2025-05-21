import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

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

# Initialisation (unique ou après confirmation)
if 'confirmed_refresh' not in st.session_state:
    st.session_state.confirmed_refresh = False
if 'order' not in st.session_state or st.session_state.confirmed_refresh:
    st.session_state.order, st.session_state.t, st.session_state.y, st.session_state.params = generate_system()
    st.session_state.confirmed_refresh = False

# Titre
st.title("🔎 Identification d'un système (réponse indicielle)")

# Affichage du graphe
fig, ax = plt.subplots()
ax.plot(st.session_state.t, st.session_state.y)
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Amplitude")
ax.set_title("Réponse indicielle aléatoire")
ax.grid(True)
st.pyplot(fig)

# Interface utilisateur
st.subheader("🎯 Estime les paramètres du système")
order_guess = st.radio("Quel est l'ordre du système affiché ?", ["Premier ordre", "Second ordre"])
K = st.number_input("K", min_value=0.0, step=0.1)
if order_guess == "Premier ordre":
    tau = st.number_input("tau", min_value=0.0, step=0.1)
else:
    omega = st.number_input("ω₀", min_value=0.0, step=0.1)
    xi = st.number_input("ξ", min_value=0.0, step=0.05)

# Vérification
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

# Double bouton pour éviter la régénération non désirée
if st.button("🔁 Générer un nouveau système"):
    st.session_state.ready_to_refresh = True

if st.session_state.get("ready_to_refresh", False):
    if st.button("🟢 Oui, je veux vraiment un autre graphe"):
        st.session_state.confirmed_refresh = True
        st.session_state.ready_to_refresh = False
        st.experimental_rerun = lambda: None  # neutralise juste au cas où
        st.stop()

st.markdown("""
Ce simulateur permet de comparer visuellement la réponse indicielle d’un système du **premier ordre** avec celle d’un **second ordre** en faisant varier les paramètres :
- **K** : gain statique
- **τ** : constante de temps (1er ordre)
- **ω₀** : pulsation propre (2nd ordre)
- **ξ** : facteur d’amortissement (2nd ordre)
""")

# Paramètres via sidebar
K = st.sidebar.slider("K (gain)", 0.5, 2.0, 1.0, 0.1)
tau = st.sidebar.slider("τ (1er ordre)", 0.1, 3.0, 1.0, 0.1)
omega_0 = st.sidebar.slider("ω₀ (2nd ordre)", 0.1, 3.0, 1.0, 0.1)
xi = st.sidebar.slider("ξ (2nd ordre)", 0.1, 3.0, 2.0, 0.1)

# Temps
t = np.linspace(0, 10, 500)

# Réponse 1er ordre
y1 = K * (1 - np.exp(-t / tau))

# Réponse 2nd ordre
if xi == 1:
    y2 = K * (1 - (1 + omega_0 * t) * np.exp(-omega_0 * t))
elif xi > 1:
    r1 = -omega_0 * (xi - np.sqrt(xi**2 - 1))
    r2 = -omega_0 * (xi + np.sqrt(xi**2 - 1))
    A = K * r2 / (r2 - r1)
    B = K - A
    y2 = K - A * np.exp(r1 * t) - B * np.exp(r2 * t)
else:
    y2 = K * (1 - (1 / np.sqrt(1 - xi**2)) * np.exp(-xi * omega_0 * t) *
              np.sin(omega_0 * np.sqrt(1 - xi**2) * t + np.arccos(xi)))

# Affichage
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(t, y1, label='Premier ordre', linestyle='--')
ax.plot(t, y2, label='Second ordre', linestyle='-')
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Amplitude")
ax.set_title("Réponses indicielle - Ordre 1 vs Ordre 2")
ax.grid(True)
ax.legend()
st.pyplot(fig)
