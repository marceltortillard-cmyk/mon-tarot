import streamlit as st
import pandas as pd
import random

# Configuration
st.set_page_config(page_title="Tarot Master Pro", layout="wide")

LISTE_AVATARS = ["🧙", "🥷", "🧛", "🤴", "👸", "🤡", "👹", "🤠", "🤖", "👻", "👽", "🦄", "🐼", "🦊", "🦁"]

# --- INITIALISATION ---
if 'bareme' not in st.session_state:
    st.session_state.bareme = {
        "base": 25, "petit_bout": 10, "poignee_s": 20, "poignee_d": 30, "poignee_t": 40, "misere": 10
    }
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

def calculer_points(contrat, pts, bouts, petit_bout, poignees, nb_j, part, preneur, miseres, chelem):
    b = st.session_state.bareme
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff = pts - seuils[bouts]
    reussi = diff >= 0
    score_base = b["base"] + abs(diff)
    if petit_bout: score_base += b["petit_bout"]
    coeffs = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}
    score_final = score_base * coeffs[contrat]
    primes_ch = {"Aucun": 0, "Grand Chelem Annoncé & Réussi": 400, "Grand Chelem Non annoncé & Réussi": 200, "Grand Chelem Annoncé & Chuté": -200, "Petit Chelem Annoncé & Réussi": 200, "Petit Chelem Non annoncé & Réussi": 100, "Petit Chelem Annoncé & Chuté": -100}
    score_final += primes_ch[chelem]
    res = {nom: 0 for nom in st.session_state.joueurs}
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
            p_pre = (score_final * 2) if reussi else -(score_final * 2)
            p_par = (score_final * 1) if reussi else -(score_final * 1)
            for j in st.session_state.joueurs:
                if j == preneur: res[j] = p_pre
                elif j == part: res[j] = p_par
                else: res[j] = -(p_pre + p_par) / 3
    val_p = {"Simple": b["poignee_s"], "Double": b["poignee_d"], "Triple": b["poignee_t"]}
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
                if j == j_m: res[j] += b["misere"] * (nb_j - 1)
                else: res[j] -= b["misere"]
    return res

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    nb_j = st.radio("Nombre de joueurs", [4, 5], horizontal=True)
    with st.expander("👤 Équipage & Noms", expanded=True):
        for i in range(nb_j):
            c1, c2 = st.columns([1, 4])
            if c1.button(st.session_state.avatars[i], key=f"btn_av_{i}"):
                changer_avatar(i)
                st.rerun()
            st.session_state.joueurs[i] = c2.text_input(f"Nom {i}", st.session_state.joueurs[i], label_visibility="collapsed")
    with st.expander("📊 Barème des points"):
        st.session_state.bareme["base"] = st.number_input("Base contrat", value=st.session_state.bareme["base"], step=5)
        st.session_state.bareme["petit_bout"] = st.number_input("Petit au bout", value=st.session_state.bareme["petit_bout"], step=5)
        st.session_state.bareme["misere"] = st.number_input("Misère", value=st.session_state.bareme["misere"], step=5)
        st.write("**Poignées :**")
        st.session_state.bareme["poignee_s"] = st.number_input("Simple", value=st.session_state.bareme["poignee_s"], step=5)
        st.session_state.bareme["poignee_d"] = st.number_input("Double", value=st.session_state.bareme["poignee_d"], step=5)
        st.session_state.bareme["poignee_t"] = st.number_input("Triple", value=st.session_state.bareme["poignee_t"], step=5)
    if st.button("🗑️ Reset la partie"):
        st.session_state.historique = []
        st.rerun()

# --- MAIN ---
st.title("🃏 Tarot Master Pro")
k = st.session_state.compteur_donne
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🏹 L'Attaque")
    preneur = st.selectbox("Preneur", st.session_state.joueurs, key=f"pre_{k}")
    contrat = st.select_slider("Enchère", ["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contre"], key=f"con_{k}")
    part = st.selectbox("Partenaire", st.session_state.joueurs + ["Au Chien / Seul"], key=f"par_{k}") if nb_j == 5 else None
with col2:
    st.markdown("### 📊 Le Résultat")
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
miseres = st.multiselect("Qui a une Misère ?", st.session_state.joueurs, key=f"mis_{k}")

st.write("")
b1, b2 = st.columns([2, 1])
if b1.button("✅ VALIDER LA DONNE", use_container_width=True, type="primary"):
    res = calculer_points(contrat, pts, bouts, petit_bout, poignees, nb_j, part, preneur, miseres, chelem)
    st.session_state.historique.append(res)
    st.session_state.compteur_donne += 1
    st.rerun()
if b2.button("↩️ Annuler", use_container_width=True) and len(st.session_state.historique) > 0:
    st.session_state.historique.pop()
    st.session_state.compteur_donne -= 1
    st.rerun()

# --- SCOREBOARD ---
if st.session_state.historique:
    df = pd.DataFrame(st.session_state.historique).cumsum()
    scores = df.iloc[-1].sort_values(ascending=False)
    st.divider()
    st.subheader(f"🏆 Classement (Donne n°{len(st.session_state.historique)})")
    c = st.columns(3)
    for i, s in enumerate([("🥇", 1), ("🥈", 0), ("🥉", 2)]):
        if len(scores) > i:
            name = scores.index[i]
            av = st.session_state.avatars[st.session_state.joueurs.index(name)]
            c[s[1]].metric(f"{s[0]} {av} {name}", f"{int(scores[i])} pts")
    st.warning(f"🟡 **SOUS-MARIN** : {scores.index[-1]} & {scores.index[-2]} 🚢")
    st.line_chart(df)
