# todo:
# filter mens dan womens
# semua data ga harus terpakai
# user bisa set bobot dan cost/benefit manual (tapi udah ada defaultnya, bisa di navbar bagian kiri dll)

import pandas as pd
import streamlit as st
import numpy as np

st.set_page_config(page_title="WP Pemilihan Sepatu Lari")
st.title("WP Pemilihan Smartphone")
st.write("Gusti Rama / 123230040 / IF-F")

st.subheader("Load data file CSV")
df = pd.read_csv("BrooksShoes.csv", sep=',')
st.dataframe(df, use_container_width=True)

# Sidebar filters
st.sidebar.header("Pengaturan WP")
gender_filter = st.sidebar.selectbox("Pilih Gender", ["All", "Men's", "Women's"])
if gender_filter != "All":
    df = df[df['Type'] == gender_filter]

# 1. Menentukan Alternatif
a = df['Name'].tolist()

support_map = {'Neutral': 1, 'Support': 2, 'Max Support': 3}
df['SupportEncoded'] = df['Support'].map(support_map)

df['GuideRailsEncoded'] = df['GuideRails'].notna().astype(int)
df['GoreTexEncoded'] = df['Gore-Tex'].notna().astype(int)

# 2. Matriks Keputusan
# x = df.drop(columns=['Name']).to_numpy()

x = df[['Price', 'SupportEncoded', 'Weight(g)', 'GuideRailsEncoded', 'GoreTexEncoded']].to_numpy()
epsilon = 1e-6
x = np.where(x == 0, epsilon, x)

criteria_names = ['Price', 'Support', 'Weight', 'GuideRails', 'Gore-Tex']
# User-defined weights
st.sidebar.subheader("Bobot Kriteria")
default_weights = [3, 5, 4, 2, 2]
w = []
for i, crit in enumerate(criteria_names):
    w.append(st.sidebar.slider(f"{crit}", 1, 5, default_weights[i]))

# 3. Membuat Cost / Benefit Per kriteria
# k = [1, 1, 1, 1, 1, 1]
k = [-1, 1,-1, 1, 1]

# 4. Membuat Bobot Per kriteria
# w = [3, 4, 4, 5, 3, 4]
# w = [3, 5, 4, 2, 2]

# 5. Normalisasi Kriteria
w_norm = [c / sum(w) for c in w]

# 6. Menghitung S(i)
# m = Jumlah Alternatif, n = jumlah kriteria
m = len(a)
n = len(w)

st.write("Matrix x (used in WP):", x) #JANGAN LUPA HAPUS, CUMAN BUAT DEBUG

s = [1]*m

for i in range(m):
    for j in range(n):
        s[i] = s[i] * (x[i][j] ** (k[j] * w_norm[j]))

# 7. Menghitung V
v = [u / sum(s) for u in s]

df_hasil = pd.DataFrame({
    'Sepatu': a,
    'WP Score': v
})

df_hasil = df_hasil.sort_values(by='WP Score', ascending=False).reset_index(drop=True)
 
# Highlight top 3
def highlight_top(val):
    color = ''
    if val == df_hasil['Sepatu'].iloc[0]:
        color = 'background-color: gold'
    elif val == df_hasil['Sepatu'].iloc[1]:
        color = 'background-color: silver'
    elif val == df_hasil['Sepatu'].iloc[2]:
        color = 'background-color: #cd7f32'
    return color

st.subheader("Hasil ranking WP")
st.dataframe(
    df_hasil.style.applymap(highlight_top, subset=['Sepatu']).format({'WP Score': '{:.6f}'}),
)

# terbaik = df_hasil['Sepatu'].iloc[0]
terbaik = a[v.index(max(v))]
st.success(f"Sepatu terbaik adalah: {terbaik} ")


csv_download = df_hasil.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Hasil Ranking sebagai CSV",
    data=csv_download,
    file_name='hasil_wp.csv',
    mime='text/csv'
)