import pandas as pd
import streamlit as st
import numpy as np

st.set_page_config(page_title="WP Pemilihan Sepatu Lari Brooks")
st.title("WP Pemilihan Sepatu Lari Brooks")
st.write("Gusti Rama / 123230040 / IF-F")
st.write("Gusti Rama / 123230040 / IF-F")

st.subheader("Load data file CSV")
df = pd.read_csv("BrooksShoes.csv", sep=',')
st.dataframe(df, use_container_width=True)

# Sidebar
st.sidebar.header("Pengaturan WP")
gender_filter = st.sidebar.selectbox("Pilih Gender", ["All", "Men's", "Women's", "Unisex"])
if gender_filter != "All":
    df = df[df['Type'] == gender_filter]

# 1. Menentukan Alternatif
a = df['Name'].tolist()

st.subheader("Data yang Digunakan")

dipakai = ['Name', 'Price', 'Type', 'Support', 'Weight(g)', 'GuideRails', 'Gore-Tex', 'DNA LOFT', 'BioMoGo DNA']
st.dataframe(df[dipakai].reset_index(drop=True), use_container_width=True)

support_map = {'Neutral': 1, 'Support': 2, 'Max Support': 3}
df['SupportEncoded'] = df['Support'].map(support_map)
df['GuideRails'] = df['GuideRails'].notna().astype(int)
df['GoreTex'] = df['Gore-Tex'].notna().astype(int)
df['DNALOFT'] = df['DNA LOFT'].notna().astype(int)
df['BioMoGoDNA'] = df['BioMoGo DNA'].notna().astype(int)

x = df[['Price', 'SupportEncoded', 'Weight(g)', 'GuideRails', 'GoreTex', 'DNALOFT', 'BioMoGoDNA']].to_numpy()
epsilon = 1e-6
x = np.where(x == 0, epsilon, x)

kriteria = ['Price', 'Support', 'Weight', 'GuideRails', 'Gore-Tex', 'DNA LOFT', 'BioMoGo DNA']

st.subheader("Matriks Keputusan (x)")
x_df = pd.DataFrame(x, columns=kriteria, index=a)
st.dataframe(x_df, use_container_width=True)

st.sidebar.subheader("Bobot Kriteria")
default_weights = [9, 7, 6, 5, 4, 5, 3]
w = []
for i, crit in enumerate(kriteria):
    w.append(st.sidebar.slider(f"{crit}", 1, 10, default_weights[i]))

# 3. Membuat Cost / Benefit Per kriteria
st.subheader("Tipe Kriteria (Cost / Benefit)")
k = [-1, 1,-1, 1, 1, 1, 1]
k_df = pd.DataFrame({'Kriteria': kriteria, 'Tipe': ['Cost' if i == -1 else 'Benefit' for i in k]})
st.dataframe(k_df)

# 5. Normalisasi Kriteria
st.subheader("Bobot Kriteria dan Normalisasi")
w_norm = [c / sum(w) for c in w]
w_df = pd.DataFrame({'Kriteria': kriteria, 'Bobot': w, 'Bobot Normalisasi': w_norm})
st.dataframe(w_df)

# 6. Menghitung S(i)
# m = Jumlah Alternatif, n = jumlah kriteria
m = len(a)
n = len(w)
s = [1]*m
for i in range(m):
    for j in range(n):
        s[i] = s[i] * (x[i][j] ** (k[j] * w_norm[j]))

s_df = pd.DataFrame({'Nama Sepatu': a, 'S(i)': s})
st.dataframe(s_df)

# 7. Menghitung V
v = [u / sum(s) for u in s]

df_hasil = pd.DataFrame({'Sepatu': a, 'WP Score': v})

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
    df_hasil.style.applymap(highlight_top, subset=['Sepatu']).format({'WP Score': '{:.6f}'}), use_container_width=True
)

# terbaik = df_hasil['Sepatu'].iloc[0]
terbaik = a[v.index(max(v))]
st.success(f"Sepatu Lari Brooks terbaik adalah: {terbaik} ")


csv_download = df_hasil.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Hasil Ranking sebagai CSV",
    data=csv_download,
    file_name='hasil_wp.csv',
    mime='text/csv'
)