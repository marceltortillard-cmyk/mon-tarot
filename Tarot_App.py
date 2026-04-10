import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Tarot Master Pro", layout="wide")

LISTE_AVATARS = ["🧙", "🥷", "🧛", "🤴", "👸", "🤡", "👹", "🤠", "🤖", "👻", "👽", "🦄", "🐼", "🦊", "🦁"]

# --- INITIALISATION ---
if 'bareme' not in st.session_state:
    st.session_state.bareme = {
        "base": 25, "petit_bout": 10, "pb_variable": False,
        "p_s": 20, "p_d": 30, "p_t": 40, "misere": 10, "mode_5j": "2/3-1/3"
    }
if 'historique' not in st.session_state:
    st.session_state.historique = []
if 'joueurs' not in st.session_state:
    st.session_state.joueurs = ["", "", "", "", ""]
if 'avatars' not in st.session_state:
    st.session_state.avatars = ["👤"] * 5
if 'compteur_donne' not in st.session_state:
    st.session_state.compteur_donne = 0

def get_nom(i):
    return st.session_state.joueurs[i] if st.session_state.joueurs[i] else f"Joueur {i+1}"

# --- FONCTION DE CALCUL ---
def calculer_points(contrat, pts_pre, bouts, pb_res, poignees, nb_j, part_nom, preneur_nom, miseres, chelem):
    b = st.session_state.bareme
    coeff = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contra": 16}[contrat]
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff = pts_pre - seuils[bouts]
    reussi = diff >= 0
    
    val_pb = b["petit_bout"] * coeff if b["pb_variable"] else b["petit_bout"]
    prime_pb = val_pb if pb_res == "Attaque" else (-val_pb if pb_res == "Défense" else 0)
    
    score_final = ((b["base"] + abs(diff)) * coeff) + prime_pb
    primes_ch = {"Aucun": 0, "Grand Chelem Réussi": 400, "Grand Chelem Chuté": -200, "Petit Chelem Réussi": 200}
    score_final += primes_ch[chelem]
    
    res = {f"S{i}": 0 for i in range(5)}
    idx_pre = [i for i, n in enumerate(st.session_state.joueurs) if get_nom(i) == preneur_nom][0]
    
    camp_att = [idx_pre]
    est_seul = (part_nom == "Seul" or part_nom == preneur_nom)
    if nb_j == 5 and not est_seul:
        idx_part = [i for i, n in enumerate(st.session_state.joueurs) if get_nom(i) == part_nom][0]
        camp_att.append(idx_part)

    if nb_j == 4 or est_seul:
        m = 3 if nb_j == 4 else 4
        tot = score_final * m if reussi else -score_final * m
        for i in range(nb_j): res[f"S{i}"] = tot if i == idx_pre else -(tot / m)
    else:
        tot = score_final * 3 if reussi else -score_final * 3
        r_pre, r_par = (0.5, 0.5) if b["mode_5j"] == "50/50" else (2/3, 1/3)
        for i in range(5):
            if i == idx_pre: res[f"S{i}"] = tot * r_pre
            elif i == idx_part: res[f"S{i}"] = tot * r_par
            else: res[f"S{i}"] = -(tot / 3)
            
    val_p = {"Simple": b["p_s"], "Double": b["p_d"], "Triple": b["p_t"]}
    for i in range(nb_j):
        nom_j = get_nom(i)
        p_type = poignees[nom_j]
        if p_type != "Aucune":
            v = val_p[p_type] if (reussi and i in camp_att) or (not reussi and i not in camp_att) else -val_p[p_type]
            for j in range(nb_j): res[f"S{j}"] += v * (nb_j - 1) if j == i else -v
            
    for m_nom in miseres:
        idx_m = [i for i, n in enumerate(st.session_state.joueurs) if get_nom(i) == m_nom][0]
        for i in range(nb_j): res[f"S{i}"] += b["misere"] * (nb_j - 1) if i == idx_m else -b["misere"]
    return res

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    nb_j = st.radio("Nombre de joueurs", [4, 5], horizontal=True)
    
    if nb_j == 5:
        st.session_state.bareme["mode_5j"] = st.radio("Partage des points (5j)", ["2/3-1/3", "50/50"], horizontal=True)

    with st.expander("👤 Noms des joueurs", expanded=False):
        for i in range(nb_j):
            c1, c2 = st.columns([1, 4])
            if c1.button(st.session_state.avatars[i], key=f"av_{i}"):
                st.session_state.avatars[i] = random.choice(LISTE_AVATARS); st.rerun()
            st.session_state.joueurs[i] = c2.text_input(f"J{i}", value=st.session_state.joueurs[i], placeholder=f"Joueur {i+1}", label_visibility="collapsed")
    
    with st.expander("📊 Barème personnalisé", expanded=True):
        st.session_state.bareme["base"] = st.number_input("Base du contrat", value=int(st.session_state.bareme["base"]), step=5)
        st.session_state.bareme["petit_bout"] = st.number_input("Petit au bout", value=int(st.session_state.bareme["petit_bout"]), step=5)
        st.session_state.bareme["pb_variable"] = st.toggle("PB lié au contrat", value=st.session_state.bareme["pb_variable"])
        st.divider()
        st.session_state.bareme["p_s"] = st.number_input("Poignée Simple", value=int(st.session_state.bareme["p_s"]), step=5)
        st.session_state.bareme["p_d"] = st.number_input("Poignée Double", value=int(st.session_state.bareme["p_d"]), step=5)
        st.session_state.bareme["p_t"] = st.number_input("Poignée Triple", value=int(st.session_state.bareme["p_t"]), step=5)
        st.session_state.bareme["misere"] = st.number_input("Misère", value=int(st.session_state.bareme["misere"]), step=5)
    
    if st.button("🗑️ Réinitialiser la partie"): st.session_state.historique = []; st.rerun()

# --- MAIN ---
st.title("🃏 Tarot Master Pro")
k = st.session_state.compteur_donne

# --- CHOIX JOUEURS ---
st.subheader("🎯 Qui a pris ?")
if f"sel_pre_{k}" not in st.session_state: st.session_state[f"sel_pre_{k}"] = get_nom(0)
c_pre = st.columns(nb_j)
for i in range(nb_j):
    nom = get_nom(i)
    is_sel = st.session_state[f"sel_pre_{k}"] == nom
    if c_pre[i].button(nom, key=f"btn_p_{i}_{k}", use_container_width=True, type="primary" if is_sel else "secondary"):
        st.session_state[f"sel_pre_{k}"] = nom; st.rerun()

if nb_j == 5:
    st.subheader("🤝 Partenaire")
    if f"sel_par_{k}" not in st.session_state: st.session_state[f"sel_par_{k}"] = "Seul"
    c_par = st.columns(5)
    for i in range(5):
        nom_j = get_nom(i)
        label = "Seul" if nom_j == st.session_state[f"sel_pre_{k}"] else nom_j
        val_btn = "Seul" if label == "Seul" else nom_j
        is_sel = st.session_state[f"sel_par_{k}"] == val_btn
        if c_par[i].button(label, key=f"btn_pa_{i}_{k}", use_container_width=True, type="primary" if is_sel else "secondary"):
            st.session_state[f"sel_par_{k}"] = val_btn; st.rerun()

st.divider()

# --- ZONE DE SCORE ---
col_s1, col_s2 = st.columns([1, 1.5])

with col_s1:
    contrat = st.select_slider("Enchère", ["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contra"], key=f"ct_{k}")
    bouts = st.radio("Nombre de Bouts", [0, 1, 2, 3], horizontal=True, key=f"bt_{k}")
    mode_saisie = st.radio("Saisir les points de :", ["Défense", "Preneur"], horizontal=True, key=f"md_{k}")
    
    if f"pts_val_{k}" not in st.session_state:
        st.session_state[f"pts_val_{k}"] = 40.0 if mode_saisie == "Défense" else 51.0

    pts_input = st.number_input(f"Points {mode_saisie}", 0.0, 91.0, float(st.session_state[f"pts_val_{k}"]), 0.5, key=f"num_{k}")
    st.session_state[f"pts_val_{k}"] = pts_input
    
    pts_pre = 91.0 - pts_input if mode_saisie == "Défense" else pts_input
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff_score = pts_pre - seuils[bouts]

with col_s2:
    st.write("### Résultat du contrat")
    r_c1, r_c2, r_c3 = st.columns([1.5, 0.8, 0.7])
    
    color = "#2ECC71" if diff_score >= 0 else "#E74C3C"
    label = "FAITE" if diff_score >= 0 else "CHUTÉE"
    
    with r_c1:
        st.markdown(f"<div style='background:{color};color:white;padding:15px;border-radius:12px;font-size:35px;font-weight:bold;text-align:center;'>{label}</div>", unsafe_allow_html=True)
    with r_c2:
        st.markdown(f"<div style='font-size:45px;font-weight:bold;color:{color};text-align:center;line-height:60px;'>{'+' if diff_score >= 0 else ''}{diff_score:g}</div>", unsafe_allow_html=True)
    with r_c3:
        # Logique des boutons corrigée pour impacter la session_state
        if st.button("➕", key=f"pl_{k}", use_container_width=True):
            st.session_state[f"pts_val_{k}"] += 1.0 if mode_saisie == "Preneur" else -1.0
            st.rerun()
        if st.button("➖", key=f"mi_{k}", use_container_width=True):
            st.session_state[f"pts_val_{k}"] -= 1.0 if mode_saisie == "Preneur" else -1.0
            st.rerun()

    st.write("---")
    st.write("#### 🎁 Bonus & Primes")
    b_c1, b_c2 = st.columns(2)
    with b_c1:
        pb_res = st.selectbox("Petit au bout", ["Aucun", "Attaque", "Défense"], key=f"pb_{k}")
    with b_c2:
        chelem = st.selectbox("Chelem", ["Aucun", "Grand Chelem Réussi", "Grand Chelem Chuté", "Petit Chelem Réussi"], key=f"ch_{k}")

st.divider()
st.subheader("🎖️ Poignées & Misères")
p_cols = st.columns(nb_j)
poignees = {}
for i in range(nb_j):
    nom_j = get_nom(i)
    with p_cols[i]:
        st.write(f"{st.session_state.avatars[i]} {nom_j}")
        poignees[nom_j] = st.selectbox("Poignée", ["Aucune", "Simple", "Double", "Triple"], key=f"po_{i}_{k}", label_visibility="collapsed")
miseres = st.multiselect("Misères", [get_nom(i) for i in range(nb_j)], key=f"mi_{k}")

if st.button("🔥 ENREGISTRER LA DONNE", use_container_width=True, type="primary"):
    res = calculer_points(contrat, pts_pre, bouts, pb_res, poignees, nb_j, st.session_state[f"sel_par_{k}"], st.session_state[f"sel_pre_{k}"], miseres, chelem)
    st.session_state.historique.append(res); st.session_state.compteur_donne += 1; st.rerun()

if st.session_state.historique:
    df = pd.DataFrame(st.session_state.historique).cumsum().rename(columns={f"S{i}": get_nom(i) for i in range(nb_j)})
    scores = df.iloc[-1].sort_values(ascending=False)
    st.header(f"🏆 CLASSEMENT (Donne {len(st.session_state.historique)})")
    for r, (n, s) in enumerate(scores.items()):
        sub = r >= nb_j - 2
        st.markdown(f"<div style='background:{'#FFF176' if sub else '#f8f9fa'};padding:15px;border-radius:10px;margin-bottom:8px;display:flex;justify-content:space-between;font-size:28px;color:black;border:1px solid #ddd'><b>#{r+1} {n}</b> <b>{int(s)} pts</b></div>", unsafe_allow_html=True)
    st.line_chart(df, height=400)