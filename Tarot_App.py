import streamlit as st
import pandas as pd
import random

# Configuration
st.set_page_config(page_title="Tarot Master Pro", layout="wide")

LISTE_AVATARS = ["🧙", "🥷", "🧛", "🤴", "👸", "🤡", "👹", "🤠", "🤖", "👻", "👽", "🦄", "🐼", "🦊", "🦁"]

# --- INITIALISATION ---
if 'bareme' not in st.session_state:
    st.session_state.bareme = {"base": 25, "petit_bout": 10, "poignee_s": 20, "poignee_d": 30, "poignee_t": 40, "misere": 10}
if 'historique' not in st.session_state:
    st.session_state.historique = []
if 'joueurs' not in st.session_state:
    st.session_state.joueurs = ["Joueur 1", "Joueur 2", "Joueur 3", "Joueur 4", "Joueur 5"]
if 'avatars' not in st.session_state:
    st.session_state.avatars = ["👤"] * 5
if 'compteur_donne' not in st.session_state:
    st.session_state.compteur_donne = 0

# --- FONCTIONS DE CALCUL ---
def calculer_points(contrat, pts_preneur, bouts, petit_resultat, poignees, nb_j, part, preneur, miseres, chelem):
    b = st.session_state.bareme
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff = pts_preneur - seuils[bouts]
    reussi = diff >= 0
    
    score_base = b["base"] + abs(diff)
    
    # Gestion du Petit au Bout (Prime multipliée par le contrat)
    prime_pb = 0
    if petit_resultat == "Gagné par l'Attaque": prime_pb = b["petit_bout"]
    elif petit_resultat == "Gagné par la Défense": prime_pb = -b["petit_bout"]
    
    coeff = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}[contrat]
    score_final = (score_base * coeff) + (prime_pb * coeff)
    
    # Primes Chelem (Fixes)
    primes_ch = {"Aucun": 0, "Grand Chelem Réussi": 400, "Grand Chelem Chuté": -200, "Petit Chelem Réussi": 200}
    score_final += primes_ch[chelem]

    res = {f"S{i}": 0 for i in range(5)}
    idx_preneur = st.session_state.joueurs.index(preneur)
    camp_att_idx = [idx_preneur]
    
    if nb_j == 5 and part != "Au Chien / Seul":
        camp_att_idx.append(st.session_state.joueurs.index(part))

    # Répartition Attaque / Défense
    if nb_j == 4:
        p_total_attaque = score_final * 3 if reussi else -score_final * 3
        for i in range(4):
            res[f"S{i}"] = p_total_attaque if i == idx_preneur else -(p_total_attaque / 3)
    else:
        # Cas à 5 joueurs
        if len(camp_att_idx) == 2: # Preneur + Partenaire
            p_total_att = score_final * 3 if reussi else -score_final * 3
            p_preneur = (p_total_att * 2 / 3)
            p_partenaire = (p_total_att * 1 / 3)
            for i in range(5):
                if i == camp_att_idx[0]: res[f"S{i}"] = p_preneur
                elif i == camp_att_idx[1]: res[f"S{i}"] = p_partenaire
                else: res[f"S{i}"] = -(p_total_att / 3)
        else: # Preneur tout seul contre 4
            p_total_att = score_final * 4 if reussi else -score_final * 4
            for i in range(5):
                res[f"S{i}"] = p_total_att if i == idx_preneur else -(p_total_att / 4)

    # Poignées & Misères (Indexées sur le Siège pour la stabilité)
    for i in range(nb_j):
        p_type = poignees[st.session_state.joueurs[i]]
        if p_type != "Aucune":
            val = {"Simple": b["poignee_s"], "Double": b["poignee_d"], "Triple": b["poignee_t"]}[p_type]
            gagne = (reussi and i in camp_att_idx) or (not reussi and i not in camp_att_idx)
            v = val if gagne else -val
            for j in range(nb_j):
                res[f"S{j}"] += v * (nb_j - 1) if j == i else -v
    
    for m_nom in miseres:
        idx_m = st.session_state.joueurs.index(m_nom)
        for i in range(nb_j):
            res[f"S{i}"] += b["misere"] * (nb_j - 1) if i == idx_m else -b["misere"]
            
    return res

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    nb_j = st.radio("Nombre de joueurs", [4, 5], horizontal=True)
    
    with st.expander("👤 Joueurs & Remplacements", expanded=True):
        for i in range(nb_j):
            c1, c2 = st.columns([1, 4])
            if c1.button(st.session_state.avatars[i], key=f"av_btn_{i}"):
                st.session_state.avatars[i] = random.choice(LISTE_AVATARS)
                st.rerun()
            st.session_state.joueurs[i] = c2.text_input(f"Siège {i+1}", st.session_state.joueurs[i], key=f"n_in_{i}")

    with st.expander("📊 Barème personnalisé"):
        st.session_state.bareme["base"] = st.number_input("Base", value=st.session_state.bareme["base"], step=5)
        st.session_state.bareme["petit_bout"] = st.number_input("Petit bout", value=st.session_state.bareme["petit_bout"], step=5)
        st.write("---")
        if st.button("🗑️ Reset la partie"):
            st.session_state.historique = []
            st.rerun()

# --- MAIN ---
st.title("🃏 Tarot Master Pro")
k = st.session_state.compteur_donne

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏹 L'Enchère")
    preneur = st.selectbox("Preneur", st.session_state.joueurs, key=f"pre_{k}")
    contrat = st.select_slider("Contrat", ["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contre"], key=f"ctr_{k}")
    part = st.selectbox("Partenaire", st.session_state.joueurs + ["Au Chien / Seul"], key=f"par_{k}") if nb_j == 5 else None

with col2:
    st.subheader("🔢 Les Points")
    # SYSTÈME DE SAISIE DOUBLE
    mode_saisie = st.radio("Saisir les points de :", ["Preneur", "Défense"], horizontal=True, key=f"mode_{k}")
    
    if mode_saisie == "Preneur":
        pts_preneur = st.number_input("Points du preneur", 0.0, 91.0, 41.0, step=0.5, key=f"ptp_{k}")
        st.caption(f"La défense a fait : {91 - pts_preneur} pts")
    else:
        pts_defense = st.number_input("Points de la défense", 0.0, 91.0, 50.0, step=0.5, key=f"ptd_{k}")
        pts_preneur = 91 - pts_defense
        st.info(f"Le preneur a fait : {pts_preneur} pts")

    bouts = st.radio("Nombre de bouts", [0, 1, 2, 3], horizontal=True, key=f"bt_{k}")
    petit_res = st.selectbox("Petit au bout", ["Aucun", "Gagné par l'Attaque", "Gagné par la Défense"], key=f"pb_{k}")
    chelem = st.selectbox("Chelem", ["Aucun", "Grand Chelem Réussi", "Grand Chelem Chuté", "Petit Chelem Réussi"], key=f"chl_{k}")

st.write("---")
st.subheader("🎖️ Poignées & Misères")
p_cols = st.columns(nb_j)
poignees = {}
for i in range(nb_j):
    with p_cols[i]:
        st.write(f"{st.session_state.avatars[i]} **{st.session_state.joueurs[i]}**")
        poignees[st.session_state.joueurs[i]] = st.selectbox("Poignée", ["Aucune", "Simple", "Double", "Triple"], key=f"poig_{i}_{k}")
miseres = st.multiselect("Misères déclarées", st.session_state.joueurs, key=f"mis_{k}")

# BOUTONS ACTIONS
st.write("")
b1, b2 = st.columns([2, 1])
if b1.button("🔥 VALIDER LA DONNE", use_container_width=True, type="primary"):
    res = calculer_points(contrat, pts_preneur, bouts, petit_res, poignees, nb_j, part, preneur, miseres, chelem)
    st.session_state.historique.append(res)
    st.session_state.compteur_donne += 1
    st.rerun()

if b2.button("↩️ Annuler dernier score", use_container_width=True) and len(st.session_state.historique) > 0:
    st.session_state.historique.pop()
    st.session_state.compteur_donne -= 1
    st.rerun()

# --- CLASSEMENT XL ---
if st.session_state.historique:
    df_brut = pd.DataFrame(st.session_state.historique).cumsum()
    df_visu = df_brut.rename(columns={f"S{i}": st.session_state.joueurs[i] for i in range(nb_j)})
    scores_finaux = df_visu.iloc[-1].sort_values(ascending=False)
    
    st.divider()
    st.header(f"🏆 CLASSEMENT (Donne n°{len(st.session_state.historique)})")
    
    for rank, (nom, score) in enumerate(scores_finaux.items()):
        # Les 2 derniers sont en jaune (Sous-marin)
        is_submarine = rank >= nb_j - 2
        bg_color = "#FFF176" if is_submarine else "#f8f9fa"
        txt_color = "#000000"
        
        st.markdown(f"""
        <div style="background-color:{bg_color}; padding:20px; border-radius:12px; margin-bottom:10px; border:2px solid #e0e0e0; display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size:32px; color:{txt_color};">
                <b>#{rank+1}</b> {nom} {"🚢" if is_submarine else ""}
            </div>
            <div style="font-size:36px; color:{txt_color}; font-weight: bold;">
                {int(score)} pts
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("📈 ÉVOLUTION")
    st.line_chart(df_visu, height=450)
