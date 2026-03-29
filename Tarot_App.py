import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Tarot Master Pro", layout="wide")

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

# --- FONCTION DE CALCUL ---
def calculer_points(contrat, pts, bouts, petit_resultat, poignees, nb_j, part, preneur, miseres, chelem):
    b = st.session_state.bareme
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff = pts - seuils[bouts]
    reussi = diff >= 0
    score_base = b["base"] + abs(diff)
    
    # Gestion du Petit au Bout
    prime_pb = 0
    if petit_resultat == "Gagné par l'Attaque": prime_pb = b["petit_bout"]
    elif petit_resultat == "Gagné par la Défense": prime_pb = -b["petit_bout"]
    
    score_final = (score_base * {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}[contrat]) + (prime_pb * {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}[contrat])
    
    primes_ch = {"Aucun": 0, "Grand Chelem Annoncé & Réussi": 400, "Grand Chelem Non annoncé & Réussi": 200, "Grand Chelem Annoncé & Chuté": -200, "Petit Chelem Annoncé & Réussi": 200, "Petit Chelem Non annoncé & Réussi": 100, "Petit Chelem Annoncé & Chuté": -100}
    score_final += primes_ch[chelem]

    res = {f"S{i}": 0 for i in range(5)}
    camp_att_idx = [st.session_state.joueurs.index(preneur)]
    if nb_j == 5 and part != "Au Chien / Seul": camp_att_idx.append(st.session_state.joueurs.index(part))

    # Répartition simplifiée
    if nb_j == 4:
        p_tot = score_final * 3 if reussi else -score_final * 3
        for i in range(4):
            res[f"S{i}"] = p_tot if i == camp_att_idx[0] else -(p_tot / 3)
    else:
        mult = 2 if len(camp_att_idx) > 1 else 4
        p_att = score_final * mult if reussi else -score_final * mult
        for i in range(5):
            if i in camp_att_idx: res[f"S{i}"] = p_att / len(camp_att_idx)
            else: res[f"S{i}"] = -(p_att / (5 - len(camp_att_idx)))

    # Poignées & Misères (Indexées sur le Siège)
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
    st.title("⚙️ Configuration")
    nb_j = st.radio("Joueurs", [4, 5], horizontal=True)
    for i in range(nb_j):
        c1, c2 = st.columns([1, 4])
        if c1.button(st.session_state.avatars[i], key=f"av_{i}"):
            st.session_state.avatars[i] = random.choice(LISTE_AVATARS)
            st.rerun()
        st.session_state.joueurs[i] = c2.text_input(f"Siège {i+1}", st.session_state.joueurs[i], key=f"nom_{i}")

# --- MAIN ---
st.title("🃏 Tarot Master Pro")
k = st.session_state.compteur_donne

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏹 Attaque")
    preneur = st.selectbox("Preneur", st.session_state.joueurs, key=f"p_{k}")
    contrat = st.select_slider("Enchère", ["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contre"], key=f"c_{k}")
    part = st.selectbox("Partenaire", st.session_state.joueurs + ["Au Chien / Seul"], key=f"pa_{k}") if nb_j == 5 else None
with col2:
    st.subheader("📊 Score")
    pts = st.number_input("Points faits", 0, 91, 41, key=f"pts_{k}")
    bouts = st.radio("Bouts", [0, 1, 2, 3], horizontal=True, key=f"b_{k}")
    petit_resultat = st.selectbox("Petit au bout", ["Aucun", "Gagné par l'Attaque", "Gagné par la Défense"], key=f"pb_{k}")
    chelem = st.selectbox("Chelem", ["Aucun", "Grand Chelem Réussi", "Grand Chelem Chuté", "Petit Chelem Réussi"], key=f"ch_{k}")

st.write("---")
p_cols = st.columns(nb_j)
poignees = {}
for i in range(nb_j):
    with p_cols[i]:
        st.write(f"{st.session_state.avatars[i]} {st.session_state.joueurs[i]}")
        poignees[st.session_state.joueurs[i]] = st.selectbox("Poignée", ["Aucune", "Simple", "Double", "Triple"], key=f"po_{i}_{k}")
miseres = st.multiselect("Misères", st.session_state.joueurs, key=f"mi_{k}")

if st.button("✅ VALIDER LA DONNE", use_container_width=True, type="primary"):
    res = calculer_points(contrat, pts, bouts, petit_resultat, poignees, nb_j, part, preneur, miseres, chelem)
    st.session_state.historique.append(res)
    st.session_state.compteur_donne += 1
    st.rerun()

# --- AFFICHAGE DES SCORES (VERSION LARGE) ---
if st.session_state.historique:
    df_brut = pd.DataFrame(st.session_state.historique).cumsum()
    # On renomme les colonnes S0, S1... avec les noms actuels des joueurs
    df_visu = df_brut.rename(columns={f"S{i}": st.session_state.joueurs[i] for i in range(nb_j)})
    
    scores_finaux = df_visu.iloc[-1].sort_values(ascending=False)
    
    st.divider()
    st.header(f"🏆 CLASSEMENT GÉNÉRAL (Donne n°{len(st.session_state.historique)})")
    
    for rank, (nom, score) in enumerate(scores_finaux.items()):
        color = "#FFF176" if rank >= nb_j - 2 else "transparent" # Jaune pour les 2 derniers
        st.markdown(f"""
        <div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:5px; border:1px solid #ddd">
            <span style="font-size:24px;"><b>#{rank+1}</b> | {nom}</span>
            <span style="float:right; font-size:24px;"><b>{int(score)} pts</b></span>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("📈 ÉVOLUTION DES SCORES")
    st.line_chart(df_visu, height=400)
