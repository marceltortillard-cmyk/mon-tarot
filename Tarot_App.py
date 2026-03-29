import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Tarot Master Pro", layout="wide")

LISTE_AVATARS = ["🧙", "🥷", "🧛", "🤴", "👸", "🤡", "👹", "🤠", "🤖", "👻", "👽", "🦄", "🐼", "🦊", "🦁"]

# --- INITIALISATION ---
if 'bareme' not in st.session_state:
    st.session_state.bareme = {
        "base": 25, "petit_bout": 10, "pb_variable": False,
        "p_s": 20, "p_d": 30, "p_t": 40, "misere": 10
    }
if 'historique' not in st.session_state:
    st.session_state.historique = []
if 'joueurs' not in st.session_state:
    st.session_state.joueurs = ["Joueur 1", "Joueur 2", "Joueur 3", "Joueur 4", "Joueur 5"]
if 'avatars' not in st.session_state:
    st.session_state.avatars = ["👤"] * 5
if 'compteur_donne' not in st.session_state:
    st.session_state.compteur_donne = 0

# --- FONCTION DE CALCUL ---
def calculer_points(contrat, pts_pre, bouts, pb_res, poignees, nb_j, part, preneur, miseres, chelem):
    b = st.session_state.bareme
    coeff = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contre": 16}[contrat]
    
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff = pts_pre - seuils[bouts]
    reussi = diff >= 0
    
    # Calcul Prime Petit au Bout
    val_pb = b["petit_bout"] * coeff if b["pb_variable"] else b["petit_bout"]
    prime_pb = 0
    if pb_res == "Attaque": prime_pb = val_pb
    elif pb_res == "Défense": prime_pb = -val_pb
    
    score_final = ( (b["base"] + abs(diff)) * coeff ) + prime_pb
    
    primes_ch = {"Aucun": 0, "Grand Chelem Réussi": 400, "Grand Chelem Chuté": -200, "Petit Chelem Réussi": 200}
    score_final += primes_ch[chelem]

    res = {f"S{i}": 0 for i in range(5)}
    idx_pre = st.session_state.joueurs.index(preneur)
    camp_att = [idx_pre]
    if nb_j == 5 and part and part != "Seul": camp_att.append(st.session_state.joueurs.index(part))

    if nb_j == 4:
        tot = score_final * 3 if reussi else -score_final * 3
        for i in range(4): res[f"S{i}"] = tot if i == idx_pre else -(tot / 3)
    else:
        if len(camp_att) == 2:
            tot = score_final * 3 if reussi else -score_final * 3
            for i in range(5):
                if i == camp_att[0]: res[f"S{i}"] = tot * 2/3
                elif i == camp_att[1]: res[f"S{i}"] = tot * 1/3
                else: res[f"S{i}"] = -(tot / 3)
        else:
            tot = score_final * 4 if reussi else -score_final * 4
            for i in range(5): res[f"S{i}"] = tot if i == idx_pre else -(tot / 4)

    val_poig = {"Simple": b["p_s"], "Double": b["p_d"], "Triple": b["p_t"]}
    for i in range(nb_j):
        p_type = poignees[st.session_state.joueurs[i]]
        if p_type != "Aucune":
            v = val_poig[p_type] if (reussi and i in camp_att) or (not reussi and i not in camp_att) else -val_poig[p_type]
            for j in range(nb_j): res[f"S{j}"] += v * (nb_j - 1) if j == i else -v
    
    for m_nom in miseres:
        idx_m = st.session_state.joueurs.index(m_nom)
        for i in range(nb_j): res[f"S{i}"] += b["misere"] * (nb_j - 1) if i == idx_m else -b["misere"]
    return res

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    nb_j = st.radio("Joueurs", [4, 5], horizontal=True)
    with st.expander("👤 Noms", expanded=False):
        for i in range(nb_j):
            c1, c2 = st.columns([1, 4])
            if c1.button(st.session_state.avatars[i], key=f"av_{i}"):
                st.session_state.avatars[i] = random.choice(LISTE_AVATARS); st.rerun()
            st.session_state.joueurs[i] = c2.text_input(f"J{i}", st.session_state.joueurs[i], label_visibility="collapsed")

    with st.expander("📊 Barème & Primes", expanded=True):
        st.session_state.bareme["base"] = st.number_input("Base", value=st.session_state.bareme["base"], step=5)
        st.session_state.bareme["petit_bout"] = st.number_input("Petit au bout", value=st.session_state.bareme["petit_bout"], step=5)
        st.session_state.bareme["pb_variable"] = st.toggle("Petit au bout vaut le prix de la prise", value=st.session_state.bareme["pb_variable"])
        st.divider()
        st.session_state.bareme["p_s"] = st.number_input("Poignée Simple", value=st.session_state.bareme["p_s"], step=5)
        st.session_state.bareme["p_d"] = st.number_input("Poignée Double", value=st.session_state.bareme["p_d"], step=5)
        st.session_state.bareme["p_t"] = st.number_input("Poignée Triple", value=st.session_state.bareme["p_t"], step=5)
        st.session_state.bareme["misere"] = st.number_input("Misère", value=st.session_state.bareme["misere"], step=5)
    
    if st.button("🗑️ Reset Partie"): st.session_state.historique = []; st.rerun()

# --- MAIN ---
st.title("🃏 Tarot Master Pro")
k = st.session_state.compteur_donne

# --- CHOIX PRENEUR ET PARTENAIRE (BOUTONS) ---
st.subheader("🏹 Qui a pris ?")
if f"sel_pre_{k}" not in st.session_state: st.session_state[f"sel_pre_{k}"] = st.session_state.joueurs[0]
if f"sel_par_{k}" not in st.session_state: st.session_state[f"sel_par_{k}"] = "Seul"

c_pre = st.columns(nb_j)
for i in range(nb_j):
    nom = st.session_state.joueurs[i]
    is_sel = st.session_state[f"sel_pre_{k}"] == nom
    if c_pre[i].button(f"🎯 {nom}" if is_sel else nom, key=f"btn_p_{i}_{k}", use_container_width=True, type="primary" if is_sel else "secondary"):
        st.session_state[f"sel_pre_{k}"] = nom; st.rerun()

if nb_j == 5:
    st.write("🤝 Partenaire :")
    c_par = st.columns(nb_j + 1)
    options_par = st.session_state.joueurs + ["Seul"]
    for i, nom in enumerate(options_par):
        is_sel = st.session_state[f"sel_par_{k}"] == nom
        if c_par[i].button(f"🤝 {nom}" if is_sel else nom, key=f"btn_pa_{i}_{k}", use_container_width=True, type="primary" if is_sel else "secondary"):
            st.session_state[f"sel_par_{k}"] = nom; st.rerun()

st.divider()
col1, col2 = st.columns(2)
with col1:
    contrat = st.select_slider("Enchère", ["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contra"], key=f"ct_{k}")
    bouts = st.radio("Bouts", [0, 1, 2, 3], horizontal=True, key=f"bt_{k}")
    pb_res = st.selectbox("Petit au bout", ["Aucun", "Attaque", "Défense"], key=f"pb_{k}")

with col2:
    mode = st.radio("Saisie :", ["Défense", "Preneur"], horizontal=True, key=f"md_{k}")
    if mode == "Défense":
        pts_def = st.number_input("Points Défense", 0.0, 91.0, 40.0, 0.5, key=f"pd_{k}")
        pts_pre = 91 - pts_def
        st.info(f"Preneur : {pts_pre} pts")
    else:
        pts_pre = st.number_input("Points Preneur", 0.0, 91.0, 51.0, 0.5, key=f"pp_{k}")
    chelem = st.selectbox("Chelem", ["Aucun", "Grand Chelem Réussi", "Grand Chelem Chuté", "Petit Chelem Réussi"], key=f"ch_{k}")

st.divider()
st.subheader("🎖️ Poignées & Misères")
p_cols = st.columns(nb_j)
poignees = {}
for i in range(nb_j):
    with p_cols[i]:
        st.write(f"{st.session_state.avatars[i]} {st.session_state.joueurs[i]}")
        poignees[st.session_state.joueurs[i]] = st.selectbox("Type", ["Aucune", "Simple", "Double", "Triple"], key=f"po_{i}_{k}", label_visibility="collapsed")
miseres = st.multiselect("Misères", st.session_state.joueurs, key=f"mi_{k}")

st.write("")
b1, b2 = st.columns([2, 1])
if b1.button("🔥 VALIDER LA DONNE", use_container_width=True, type="primary"):
    res = calculer_points(contrat, pts_pre, bouts, pb_res, poignees, nb_j, st.session_state[f"sel_par_{k}"], st.session_state[f"sel_pre_{k}"], miseres, chelem)
    st.session_state.historique.append(res); st.session_state.compteur_donne += 1; st.rerun()
if b2.button("↩️ Annuler", use_container_width=True) and st.session_state.historique:
    st.session_state.historique.pop(); st.session_state.compteur_donne -= 1; st.rerun()

if st.session_state.historique:
    df = pd.DataFrame(st.session_state.historique).cumsum().rename(columns={f"S{i}": st.session_state.joueurs[i] for i in range(nb_j)})
    scores = df.iloc[-1].sort_values(ascending=False)
    st.header(f"🏆 CLASSEMENT (Donne {len(st.session_state.historique)})")
    for r, (n, s) in enumerate(scores.items()):
        sub = r >= nb_j - 2
        st.markdown(f"<div style='background:{'#FFF176' if sub else '#f8f9fa'};padding:20px;border-radius:10px;margin-bottom:8px;display:flex;justify-content:space-between;font-size:30px;color:black'><b>#{r+1} {n}</b> <b>{int(s)} pts</b></div>", unsafe_allow_html=True)
    st.line_chart(df, height=400)
