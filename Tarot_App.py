import streamlit as st
import pandas as pd

# Configuration
st.set_page_config(page_title="Tarot Master - Club des Experts", layout="wide")

# --- INITIALISATION ---
if 'historique' not in st.session_state:
    st.session_state.historique = []
if 'joueurs' not in st.session_state:
    st.session_state.joueurs = ["Joueur 1", "Joueur 2", "Joueur 3", "Joueur 4", "Joueur 5"]
if 'avatars' not in st.session_state:
    st.session_state.avatars = ["👤", "👤", "👤", "👤", "👤"]
if 'scores_cumules' not in st.session_state:
    st.session_state.scores_cumules = {nom: 0 for nom in st.session_state.joueurs}

# --- FONCTION DE CALCUL ---
def calculer_points(contrat, points_faits, bouts, petit_au_bout, poignee, nb_joueurs, type_partage, partenaire, preneur, miseres, chelem_type):
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    seuil = seuils[bouts]
    diff = points_faits - seuil
    reussi = diff >= 0
    score_base = 25 + abs(diff)
    if petit_au_bout: score_base += 10
    coeffs = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}
    score_final = score_base * coeffs[contrat]
    val_poignee = {"Aucune": 0, "Simple": 20, "Double": 30, "Triple": 40}
    score_final += val_poignee[poignee]
    primes_chelem = {
        "Aucun": 0, "Grand Chelem Annoncé & Réussi": 400, "Grand Chelem Non annoncé & Réussi": 200,
        "Grand Chelem Annoncé & Chuté": -200, "Petit Chelem Annoncé & Réussi": 200,
        "Petit Chelem Non annoncé & Réussi": 100, "Petit Chelem Annoncé & Chuté": -100
    }
    score_final += primes_chelem[chelem_type]
    resultats = {nom: 0 for nom in st.session_state.joueurs}
    if nb_joueurs == 4:
        p_preneur = score_final * 3 if reussi else -score_final * 3
        for j in st.session_state.joueurs:
            resultats[j] = p_preneur if j == preneur else -(p_preneur / 3)
    elif nb_joueurs == 5:
        if partenaire == preneur or partenaire == "Au Chien / Seul":
            p_preneur = score_final * 4 if reussi else -score_final * 4
            for j in st.session_state.joueurs:
                resultats[j] = p_preneur if j == preneur else -(p_preneur / 4)
        else:
            mult = 1.5 if type_partage == "50/50" else 2
            p_preneur = (score_final * mult) if reussi else -(score_final * mult)
            p_partenaire = (score_final * (3 - mult)) if reussi else -(score_final * (3 - mult))
            for j in st.session_state.joueurs:
                if j == preneur: resultats[j] = p_preneur
                elif j == partenaire: resultats[j] = p_partenaire
                else: resultats[j] = -(p_preneur + p_partenaire) / 3
    if miseres:
        for j_m in miseres:
            for j in st.session_state.joueurs:
                if j == j_m: resultats[j] += 10 * (nb_joueurs - 1)
                else: resultats[j] -= 10
    return resultats

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("👥 Joueurs & Avatars")
    nb_joueurs = st.radio("Format", [4, 5], horizontal=True)
    
    for i in range(nb_joueurs):
        col_av, col_nom = st.columns([1, 3])
        with col_av:
            st.session_state.avatars[i] = st.text_input(f"Avat{i}", st.session_state.avatars[i], key=f"av_{i}")
        with col_nom:
            ancien_nom = st.session_state.joueurs[i]
            n_nom = st.text_input(f"Nom {i+1}", ancien_nom, key=f"nom_{i}")
            if n_nom != ancien_nom:
                st.session_state.scores_cumules[n_nom] = st.session_state.scores_cumules.pop(ancien_nom, 0)
                st.session_state.joueurs[i] = n_nom

    if st.button("🔄 Reset Total"):
        st.session_state.historique = []
        st.session_state.scores_cumules = {nom: 0 for nom in st.session_state.joueurs}
        st.rerun()

# --- INTERFACE SAISIE ---
st.title("🃏 Tarot Master : Version Expert")
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("L'Enchère")
    preneur = st.selectbox("Preneur", st.session_state.joueurs)
    contrat = st.select_slider("Contrat", options=["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contre"])
    partenaire = st.selectbox("Partenaire", st.session_state.joueurs + ["Au Chien / Seul"]) if nb_joueurs == 5 else None
    mode_partage = st.radio("Partage", ["2/3-1/3", "50/50"], horizontal=True) if nb_joueurs == 5 else None
with c2:
    st.subheader("Le Jeu")
    points_faits = st.number_input("Points faits", 0, 91, 41)
    bouts = st.radio("Bouts", [0, 1, 2, 3], horizontal=True)
    poignee = st.selectbox("Poignée", ["Aucune", "Simple", "Double", "Triple"])
with c3:
    st.subheader("Primes")
    petit_au_bout = st.checkbox("Petit au bout")
    chelem = st.selectbox("Chelem", ["Aucun", "Grand Chelem Annoncé & Réussi", "Grand Chelem Non annoncé & Réussi", "Grand Chelem Annoncé & Chuté", "Petit Chelem Annoncé & Réussi", "Petit Chelem Non annoncé & Réussi", "Petit Chelem Annoncé & Chuté"])
    miseres = st.multiselect("Misères", st.session_state.joueurs)

if st.button("🔥 ENREGISTRER LA DONNE", use_container_width=True):
    res = calculer_points(contrat, points_faits, bouts, petit_au_bout, poignee, nb_joueurs, mode_partage, partenaire, preneur, miseres, chelem)
    donne_data = {"Donne": len(st.session_state.historique) + 1}
    for j in st.session_state.joueurs:
        donne_data[j] = res[j]
        st.session_state.scores_cumules[j] += res[j]
    st.session_state.historique.append(donne_data)
    st.rerun()

# --- AFFICHAGE VISUEL ---
if st.session_state.historique:
    df_scores = pd.DataFrame([st.session_state.scores_cumules]).T.rename(columns={0: 'Points'}).sort_values('Points', ascending=False)
    joueurs_classes = df_scores.index.tolist()
    
    # Trouver l'avatar correspondant au nom
    def get_av(nom):
        try:
            idx = st.session_state.joueurs.index(nom)
            return st.session_state.avatars[idx]
        except: return "👤"

    st.divider()
    st.subheader("🏆 Podium des Experts")
    p1, p2, p3 = st.columns(3)
    with p2: # 1er
        st.metric(f"🥇 {get_av(joueurs_classes[0])} {joueurs_classes[0]}", f"{int(df_scores.loc[joueurs_classes[0], 'Points'])} pts")
    with p1: # 2eme
        if len(joueurs_classes) > 1:
            st.metric(f"🥈 {get_av(joueurs_classes[1])} {joueurs_classes[1]}", f"{int(df_scores.loc[joueurs_classes[1], 'Points'])} pts")
    with p3: # 3eme
        if len(joueurs_classes) > 2:
            st.metric(f"🥉 {get_av(joueurs_classes[2])} {joueurs_classes[2]}", f"{int(df_scores.loc[joueurs_classes[2], 'Points'])} pts")

    st.divider()
    # --- SOUS-MARIN JAUNE ---
    derniers = df_scores.tail(2)
    st.warning(f"🟡 **SOUS-MARIN JAUNE EN IMMERSION** 🚢\n\n**Équipage :** {get_av(derniers.index[0])} {derniers.index[0]} & {get_av(derniers.index[1])} {derniers.index[1]} (Glou glou...)")

    st.subheader("📈 Évolution")
    df_hist = pd.DataFrame(st.session_state.historique).set_index('Donne')[st.session_state.joueurs].cumsum()
    st.line_chart(df_hist)
