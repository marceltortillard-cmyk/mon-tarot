import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import segno
from io import BytesIO

# Configuration de la page
st.set_page_config(page_title="Tarot Pro - Experts & Remplaçants", layout="wide")

# --- INITIALISATION DES VARIABLES ---
if 'historique' not in st.session_state:
    st.session_state.historique = []
if 'joueurs' not in st.session_state:
    st.session_state.joueurs = ["Joueur 1", "Joueur 2", "Joueur 3", "Joueur 4", "Joueur 5"]
if 'scores_cumules' not in st.session_state:
    st.session_state.scores_cumules = {nom: 0 for nom in st.session_state.joueurs}

# --- FONCTION DE CALCUL ---
def calculer_points(contrat, points_faits, bouts, petit_au_bout, poignee, nb_joueurs, type_partage, partenaire, preneur, miseres, chelem_type):
    # Seuils de réussite
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    seuil = seuils[bouts]
    
    diff = points_faits - seuil
    reussi = diff >= 0
    
    # Base standard : 25 + points de gain
    score_base = 25 + abs(diff)
    
    # Bonus Petit au bout
    if petit_au_bout:
        score_base += 10
        
    # Coefficients avec doublement
    coeffs = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}
    score_final = score_base * coeffs[contrat]
    
    # Bonus Poignée (Prime fixe)
    val_poignee = {"Aucune": 0, "Simple": 20, "Double": 30, "Triple": 40}
    score_final += val_poignee[poignee]
    
    # Gestion des Chelems (Correction : Grand et Petit)
    primes_chelem = {
        "Aucun": 0,
        "Grand Chelem Annoncé & Réussi": 400,
        "Grand Chelem Non annoncé & Réussi": 200,
        "Grand Chelem Annoncé & Chuté": -200,
        "Petit Chelem Annoncé & Réussi": 200,
        "Petit Chelem Non annoncé & Réussi": 100,
        "Petit Chelem Annoncé & Chuté": -100
    }
    score_final += primes_chelem[chelem_type]

    resultats = {nom: 0 for nom in st.session_state.joueurs}
    
    # Répartition Attaque / Défense
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

    # Misères
    if miseres:
        for joueur_misere in miseres:
            for j in st.session_state.joueurs:
                if j == joueur_misere: resultats[j] += 10 * (nb_joueurs - 1)
                else: resultats[j] -= 10
                
    return resultats

# --- BARRE LATÉRALE (GESTION DES JOUEURS) ---
with st.sidebar:
    st.header("👥 Gestion des Joueurs")
    nb_joueurs = st.radio("Format de la partie", [4, 5], horizontal=True)
    
    st.subheader("Noms & Remplacements")
    nouveaux_noms = []
    for i in range(nb_joueurs):
        ancien_nom = st.session_state.joueurs[i]
        n_nom = st.text_input(f"Siège {i+1}", ancien_nom, key=f"input_{i}")
        nouveaux_noms.append(n_nom)
        
        # Si le nom change, on transfère le score
        if n_nom != ancien_nom:
            st.session_state.scores_cumules[n_nom] = st.session_state.scores_cumules.pop(ancien_nom)
            st.session_state.joueurs[i] = n_nom

    if st.button("🔄 Réinitialiser tous les scores"):
        st.session_state.historique = []
        st.session_state.scores_cumules = {nom: 0 for nom in st.session_state.joueurs}
        st.rerun()

# --- ZONE DE SAISIE ---
st.title("🃏 Tarot Master : Version Expert")
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("L'Enchère")
    preneur = st.selectbox("Preneur", st.session_state.joueurs)
    contrat = st.select_slider("Enchère", options=["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contre"])
    if nb_joueurs == 5:
        partenaire = st.selectbox("Partenaire", st.session_state.joueurs + ["Au Chien / Seul"])
        mode_partage = st.radio("Partage", ["2/3-1/3", "50/50"], horizontal=True)
    else: partenaire, mode_partage = None, None

with c2:
    st.subheader("Le Jeu")
    points_faits = st.number_input("Points faits", 0, 91, 41)
    bouts = st.radio("Bouts", [0, 1, 2, 3], horizontal=True)
    poignee = st.selectbox("Poignée", ["Aucune", "Simple", "Double", "Triple"])

with c3:
    st.subheader("Primes & Bonus")
    petit_au_bout = st.checkbox("Petit au bout")
    chelem = st.selectbox("Chelem", [
        "Aucun", 
        "Grand Chelem Annoncé & Réussi", "Grand Chelem Non annoncé & Réussi", "Grand Chelem Annoncé & Chuté",
        "Petit Chelem Annoncé & Réussi", "Petit Chelem Non annoncé & Réussi", "Petit Chelem Annoncé & Chuté"
    ])
    miseres = st.multiselect("Misères (10 pts)", st.session_state.joueurs)

if st.button("🔥 ENREGISTRER LA DONNE", use_container_width=True):
    res = calculer_points(contrat, points_faits, bouts, petit_au_bout, poignee, nb_joueurs, mode_partage, partenaire, preneur, miseres, chelem)
    donne_data = {"Donne": len(st.session_state.historique) + 1}
    for j in st.session_state.joueurs:
        donne_data[j] = res[j]
        st.session_state.scores_cumules[j] += res[j]
    st.session_state.historique.append(donne_data)
    st.rerun()

# --- CLASSEMENT & PODIUM ---
st.divider()
col_tab, col_graph = st.columns([1, 1])

with col_tab:
    st.subheader("🏆 Classement")
    df_scores = pd.DataFrame([st.session_state.scores_cumules]).T.rename(columns={0: 'Points'}).sort_values('Points', ascending=False)
    st.table(df_scores)

with col_graph:
    st.subheader("📈 Évolution")
    if st.session_state.historique:
        df_hist = pd.DataFrame(st.session_state.historique).set_index('Donne')[st.session_state.joueurs].cumsum()
        st.line_chart(df_hist)

# --- LE SOUS-MARIN ---
if len(st.session_state.historique) > 0:
    st.divider()
    derniers = df_scores.tail(2).index.tolist()
    st.subheader("🤿 Le Sous-Marin")
    st.error(f"Équipage des abysses : **{derniers[0]}** & **{derniers[1]}**")
    st.markdown("🚢 *Glou glou glou...*")