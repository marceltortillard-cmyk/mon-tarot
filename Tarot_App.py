import streamlit as st
import pandas as pd
import random

# Configuration
st.set_page_config(page_title="Tarot Master Pro", layout="wide")

# Liste d'avatars possibles
LISTE_AVATARS = ["🧙", "🥷", "🧛", "🤴", "👸", "🤡", "👹", "🤠", "🤖", "👻", "👽", "🦄", "🐼", "🦊", "🦁"]

# --- INITIALISATION ---
if 'historique' not in st.session_state:
    st.session_state.historique = []
if 'joueurs' not in st.session_state:
    st.session_state.joueurs = [f"Joueur {i+1}" for i in range(5)]
if 'avatars' not in st.session_state:
    st.session_state.avatars = ["👤"] * 5
if 'compteur_donne' not in st.session_state:
    st.session_state.compteur_donne = 0

# --- FONCTIONS ---
def changer_avatar(idx):
    st.session_state.avatars[idx] = random.choice(LISTE_AVATARS)

def calculer_points(contrat, pts, bouts, petit_bout, poignees, nb_j, partage, part, preneur, miseres, chelem):
    # Base du calcul
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff = pts - seuils[bouts]
    reussi = diff >= 0
    score_base = 25 + abs(diff)
    if petit_bout: score_base += 10
    
    coeffs = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}
    score_final = score_base * coeffs[contrat]
    
    # Primes Chelem
    primes_ch = {"Aucun": 0, "Grand Chelem Annoncé & Réussi": 400, "Grand Chelem Non annoncé & Réussi": 200, "Grand Chelem Annoncé & Chuté": -200, "Petit Chelem Annoncé & Réussi": 200, "Petit Chelem Non annoncé & Réussi": 100, "Petit Chelem Annoncé & Chuté": -100}
    score_final += primes_ch[chelem]

    res = {nom: 0 for nom in st.session_state.joueurs}
    
    # Partage Attaque / Défense
    if nb_j == 4:
        p_tot = score_final * 3 if reussi else -score_final * 3
        for j in st.session_state.joueurs:
            res[j] = p_tot if j == preneur else -(p_tot / 3)
    else:
        if part == preneur or part == "Au Chien / Seul":
            p_tot = score_final * 4 if reussi else -score_final * 4
            for j in st.session_state.joueurs:
                res[j] = p_tot if j == preneur else -(p_tot / 4)
        else:
            m = 1.5 if partage == "50/50" else 2
            p_pre = (score_final * m) if reussi else -(score_final * m)
            p_par = (score_final * (3 - m)) if reussi else -(score_final * (3 - m))
            for j in st.session_state.joueurs:
                if j == preneur: res[j] = p_pre
                elif j == part: res[j] = p_par
                else: res[j] = -(p_pre + p_par) / 3

    # Poignées & Misères
    val_p = {"Simple": 20, "Double": 30, "Triple": 40}
    for j_nom, p_type in poignees.items():
        if p_type != "Aucune":
            camp_att = [preneur, part] if nb_j == 5 else [preneur]
            gagne = (reussi and j_nom in camp_att) or (not reussi and j_nom not in camp_att)
            val = val_p[p_type] if gagne else -val_p[p_type]
            for j in st.session_state.joueurs:
                if j == j_nom: res[j] += val * (nb_j - 1)
                else: res[j] -= val
    if miseres:
        for j_m in miseres:
            for j in st.session_state.joueurs:
                if j == j_m: res[j] += 10 * (nb_j - 1)
                else: res[j] -= 10
    return res

# --- SIDEBAR ---
with st.sidebar:
    st.title("👥 Joueurs")
    nb_j = st.radio("Format", [4, 5], horizontal=True)
    for i in range(nb_j):
        c1, c2 = st.columns([1, 4])
        if c1.button(st.session_state.avatars[i], key=f"btn_av_{i}"):
            changer_avatar(i)
            st.rerun()
        st.session_state.joueurs[i] = c2.text_input(f"Nom {i}", st.session_state.joueurs[i], label_visibility="collapsed")
    if st.button("🗑️ Reset Scores"):
        st.session_state.historique = []
        st.rerun()

# --- MAIN ---
st.title("🃏 Tarot Master")
k = st.session_state.compteur_donne # Clé pour reset les menus

col1, col2 = st.columns(2)
with col1:
    preneur = st.selectbox("Preneur", st.session_state.joueurs, key=f"pre_{k}")
    contrat = st.select_slider("Enchère", ["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contre"], key=f"con_{k}")
    part = st.selectbox("Partenaire", st.session_state.joueurs + ["Au Chien / Seul"], key=f"par_{k}") if nb_j == 5 else None
with col2:
    pts = st.number_input("Points faits", 0, 91, 41, key=f"pts_{k}")
    bouts = st.radio("Bouts", [0, 1, 2, 3], horizontal=True, key=f"bt_{k}")
    petit_bout = st.checkbox("Petit au bout", key=f"pb_{k}")
    chelem = st.selectbox("Chelem", ["Aucun", "Grand Chelem Annoncé & Réussi", "Grand Chelem Non annoncé & Réussi", "Grand Chelem Annoncé & Chuté", "Petit Chelem Annoncé & Réussi", "Petit Chelem Non annoncé & Réussi", "Petit Chelem Annoncé & Chuté"], key=f"chl_{k}")

st.write("### 🎖️ Poignées & Misères")
p_cols = st.columns(nb_j)
poignees = {}
for i in range(nb_j):
    with p_cols[i]:
        st.write(f"{st.session_state.avatars[i]} **{st.session_state.joueurs[i]}**")
        poignees[st.session_state.joueurs[i]] = st.selectbox("P.", ["Aucune", "Simple", "Double", "Triple"], key=f"p_val_{i}_{k}")
miseres = st.multiselect("Misères", st.session_state.joueurs, key=f"mis_{k}")

if st.button("✅ VALIDER LA DONNE", use_container_width=True, type="primary"):
    res = calculer_points(contrat, pts, bouts, petit_bout, poignees, nb_j, "2/3-1/3", part, preneur, miseres, chelem)
    st.session_state.historique.append(res)
    st.session_state.compteur_donne += 1
    st.rerun()

# --- SCOREBOARD ---
if st.session_state.historique:
    df = pd.DataFrame(st.session_state.historique).cumsum()
    scores = df.iloc[-1].sort_values(ascending=False)
    st.divider()
    st.subheader("🏆 Classement")
    c = st.columns(3)
    for i, s in enumerate([("🥇", 1), ("🥈", 0), ("🥉", 2)]):
        if len(scores) > i:
            name = scores.index[i]
            av = st.session_state.avatars[st.session_state.joueurs.index(name)]
            c[s[1]].metric(f"{s[0]} {av} {name}", f"{int(scores[i])} pts")
    st.warning(f"🟡 **SOUS-MARIN** : {scores.index[-1]} & {scores.index[-2]} 🚢")
    st.line_chart(df)
