import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Tarot Master Pro", layout="wide")

# --- INITIALISATION ---
if 'bareme' not in st.session_state:
    st.session_state.bareme = {"base": 25, "petit_bout": 10, "pb_variable": False, "p_s": 20, "p_d": 30, "p_t": 40, "misere": 10, "mode_5j": "2/3-1/3"}
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

# --- FONCTIONS DE MISE À JOUR ---
def modif_pts(delta, mode):
    # Delta est toujours appliqué à la valeur affichée (Défense ou Preneur)
    st.session_state[f"pts_bruts_{st.session_state.compteur_donne}"] += delta

# --- CALCUL ---
def calculer_points(contrat, pts_pre, bouts, pb_res, poignees, nb_j, part_nom, preneur_nom, miseres, chelem):
    b = st.session_state.bareme
    coeff = {"Petite": 1, "Pousse": 2, "Garde": 4, "Garde Sans": 8, "Garde Contra": 16}[contrat]
    seuils = {0: 56, 1: 51, 2: 41, 3: 36}
    diff = int(pts_pre) - seuils[bouts]
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
        st.session_state.bareme["mode_5j"] = st.radio("Partage (5j)", ["2/3-1/3", "50/50"], horizontal=True)
    with st.expander("👤 Noms"):
        for i in range(nb_j):
            st.session_state.joueurs[i] = st.text_input(f"Joueur {i+1}", value=st.session_state.joueurs[i], placeholder=f"Joueur {i+1}")
    with st.expander("📊 Barème", expanded=True):
        for key in ["base", "petit_bout", "p_s", "p_d", "p_t", "misere"]:
            st.session_state.bareme[key] = st.number_input(key.replace('_',' ').title(), value=int(st.session_state.bareme[key]), step=1)
        st.session_state.bareme["pb_variable"] = st.toggle("PB lié au contrat", value=st.session_state.bareme["pb_variable"])
    if st.button("🗑️ Reset Partie"): st.session_state.historique = []; st.rerun()

# --- MAIN ---
k = st.session_state.compteur_donne
st.subheader("🎯 Qui a pris ?")
if f"pre_{k}" not in st.session_state: st.session_state[f"pre_{k}"] = get_nom(0)
cp = st.columns(nb_j)
for i in range(nb_j):
    n = get_nom(i)
    if cp[i].button(n, key=f"bp_{i}_{k}", use_container_width=True, type="primary" if st.session_state[f"pre_{k}"] == n else "secondary"):
        st.session_state[f"pre_{k}"] = n; st.rerun()

if nb_j == 5:
    st.subheader("🤝 Partenaire")
    if f"par_{k}" not in st.session_state: st.session_state[f"par_{k}"] = "Seul"
    cpa = st.columns(5)
    for i in range(5):
        n_j = get_nom(i)
        lbl = "Seul" if n_j == st.session_state[f"pre_{k}"] else n_j
        if cpa[i].button(lbl, key=f"bpa_{i}_{k}", use_container_width=True, type="primary" if st.session_state[f"par_{k}"] == (n_j if lbl != "Seul" else "Seul") else "secondary"):
            st.session_state[f"par_{k}"] = (n_j if lbl != "Seul" else "Seul"); st.rerun()

st.divider()
col1, col2 = st.columns([1, 1.5])

with col1:
    contrat = st.select_slider("Enchère", ["Petite", "Pousse", "Garde", "Garde Sans", "Garde Contra"], key=f"ct_{k}")
    bouts = st.radio("Bouts", [0, 1, 2, 3], horizontal=True, key=f"bt_{k}")
    mode_s = st.radio("Saisie :", ["Défense", "Preneur"], horizontal=True, key=f"md_{k}")
    
    if f"pts_bruts_{k}" not in st.session_state: st.session_state[f"pts_bruts_{k}"] = 40
    
    pts_saisie = st.number_input(f"Points {mode_s}", 0, 91, int(st.session_state[f"pts_bruts_{k}"]), step=1, key=f"num_{k}")
    st.session_state[f"pts_bruts_{k}"] = pts_saisie
    
    # On calcule TOUJOURS les points du preneur pour le résultat FAITE/CHUTÉE
    pts_pre = 91 - pts_saisie if mode_s == "Défense" else pts_saisie
    diff = pts_pre - {0: 56, 1: 51, 2: 41, 3: 36}[bouts]

with col2:
    st.write("### Résultat")
    cr1, cr2, cr3 = st.columns([1.5, 0.8, 0.7])
    clr = "#2ECC71" if diff >= 0 else "#E74C3C"
    with cr1: st.markdown(f"<div style='background:{clr};color:white;padding:15px;border-radius:12px;font-size:35px;font-weight:bold;text-align:center;'>{'FAITE' if diff >= 0 else 'CHUTÉE'}</div>", unsafe_allow_html=True)
    with cr2: st.markdown(f"<div style='font-size:45px;font-weight:bold;color:{clr};text-align:center;line-height:60px;'>{'+' if diff >= 0 else ''}{diff}</div>", unsafe_allow_html=True)
    with cr3:
        st.button("➕", key=f"p_{k}", on_click=modif_pts, args=(1, mode_s), use_container_width=True)
        st.button("➖", key=f"m_{k}", on_click=modif_pts, args=(-1, mode_s), use_container_width=True)
    st.write("---")
    st.write("#### 🎁 Bonus")
    cb1, cb2 = st.columns(2)
    pb_res = cb1.selectbox("Petit au bout", ["Aucun", "Attaque", "Défense"], key=f"pb_{k}")
    chelem = cb2.selectbox("Chelem", ["Aucun", "Grand Chelem Réussi", "Grand Chelem Chuté", "Petit Chelem Réussi"], key=f"ch_{k}")

st.divider()
st.subheader("🎖️ Poignées & Misères")
p_cols = st.columns(nb_j)
poignees = {}
for i in range(nb_j):
    nom = get_nom(i)
    p_cols[i].write(f"**{nom}**")
    poignees[nom] = p_cols[i].selectbox(f"Poignée {i}", ["Aucune", "Simple", "Double", "Triple"], key=f"po_{i}_{k}", label_visibility="collapsed")
miseres = st.multiselect("Qui a une Misère ?", [get_nom(i) for i in range(nb_j)], key=f"mi_{k}")

if st.button("🔥 ENREGISTRER LA DONNE", use_container_width=True, type="primary"):
    res = calculer_points(contrat, pts_pre, bouts, pb_res, poignees, nb_j, st.session_state[f"par_{k}"], st.session_state[f"pre_{k}"], miseres, chelem)
    st.session_state.historique.append(res); st.session_state.compteur_donne += 1; st.rerun()

if st.session_state.historique:
    df = pd.DataFrame(st.session_state.historique).cumsum().rename(columns={f"S{i}": get_nom(i) for i in range(nb_j)})
    st.header(f"🏆 CLASSEMENT (Donne {len(st.session_state.historique)})")
    sc = df.iloc[-1].sort_values(ascending=False)
    for r, (n, s) in enumerate(sc.items()):
        st.markdown(f"<div style='background:{'#FFF176' if r >= nb_j-2 else '#f8f9fa'};padding:15px;border-radius:10px;margin-bottom:8px;display:flex;justify-content:space-between;font-size:28px;color:black;'><b>#{r+1} {n}</b> <b>{int(s)}</b></div>", unsafe_allow_html=True)
    st.line_chart(df)