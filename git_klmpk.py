#JAWABAN NO 17
df['kategori_dm'] = pd.cut(
    df['jumlah_penderita_dm'],
    bins=[0, 50000, 100000, float('inf')],
    labels=['Rendah', 'Sedang', 'Tinggi'],
    right=False
)

df[['jumlah_penderita_dm', 'kategori_dm']].head()

#JAWABAN NO 18
df['persentase_tahun'] = (
    df['jumlah_penderita_dm'] /
    df.groupby('tahun')['jumlah_penderita_dm'].transform('sum')
) * 100

df[['nama_kabupaten_kota', 'tahun', 'persentase_tahun']].head()

#JAWABAN NO 19
tabel_ringkas = df.groupby('tahun').agg(
    total_jumlah_penderita_dm=('jumlah_penderita_dm', 'sum'),
    jumlah_kabupaten_kota=('nama_kabupaten_kota', 'nunique')
).reset_index()

tabel_ringkas

#JAWABAN NO 20
import matplotlib.pyplot as plt

df_2019 = df[df['tahun'] == 2019]

plt.figure()
plt.bar(df_2019['nama_kabupaten_kota'], df_2019['jumlah_penderita_dm'])
plt.xticks(rotation=90)
plt.xlabel('Nama Kabupaten/Kota')
plt.ylabel('Jumlah Penderita DM')
plt.title('Jumlah Penderita DM per Kabupaten/Kota Tahun 2019')
plt.tight_layout()
plt.show()

#JAWABAN NO 21
total_per_tahun = df.groupby('tahun')['jumlah_penderita_dm'].sum()

plt.figure()
plt.plot(total_per_tahun.index, total_per_tahun.values, marker='o')
plt.xlabel('Tahun')
plt.ylabel('Total Jumlah Penderita DM')
plt.title('Total Jumlah Penderita DM Jawa Barat per Tahun')
plt.show()

#JAWABAN NO 22
top10_2019 = (
    df_2019
    .sort_values(by='jumlah_penderita_dm', ascending=False)
    .head(10)
)

plt.figure()
plt.barh(top10_2019['nama_kabupaten_kota'], top10_2019['jumlah_penderita_dm'])
plt.xlabel('Jumlah Penderita DM')
plt.ylabel('Nama Kabupaten/Kota')
plt.title('10 Kabupaten/Kota dengan Penderita DM Tertinggi Tahun 2019')
plt.gca().invert_yaxis()
plt.show()

#JAWABAN NO 23
kategori_2019 = (
    df_2019
    .groupby('kategori_dm')['jumlah_penderita_dm']
    .sum()
)

plt.figure()
plt.pie(
    kategori_2019.values,
    labels=kategori_2019.index,
    autopct='%1.1f%%'
)
plt.title('Proporsi Penderita DM Berdasarkan Kategori Tahun 2019')
plt.show()

#JAWABAN NO 24
tahun_terakhir = sorted(df['tahun'].unique())[-3:]

total_3_tahun = (
    df[df['tahun'].isin(tahun_terakhir)]
    .groupby('tahun')['jumlah_penderita_dm']
    .sum()
)

plt.figure()
plt.bar(total_3_tahun.index, total_3_tahun.values)
plt.xlabel('Tahun')
plt.ylabel('Total Jumlah Penderita DM')
plt.title('Perbandingan Total Penderita DM (3 Tahun Terakhir)')
plt.show()

#JAWABAN NO 25
#a. Kabupaten/kota dengan penderita DM tertinggi
#Berdasarkan grafik bar dan bar horizontal tahun 2019, terlihat bahwa kabupaten/kota dengan jumlah penderita DM tertinggi adalah daerah dengan populasi besar (umumnya kota/kabupaten metropolitan). Jika dilihat pada beberapa tahun, daerah ini cenderung konsisten berada di peringkat atas, meskipun nilai pastinya berubah tiap tahun.

#b. Tren jumlah penderita DM di Jawa Barat
#Grafik garis menunjukkan bahwa total jumlah penderita DM di Jawa Barat cenderung meningkat dari tahun ke tahun. Hal ini mengindikasikan adanya peningkatan kasus DM, yang bisa disebabkan oleh pertumbuhan penduduk, perubahan pola hidup, atau peningkatan pelaporan data kesehatan.

#c. Sebaran kategori Rendah / Sedang / Tinggi
#Dari pie chart kategori tahun 2019:
#Kategori Sedang dan Tinggi mendominasi total penderita DM
#Kabupaten/kota dengan kategori Rendah relatif lebih sedikit kontribusinya
#Hal ini menunjukkan bahwa sebagian besar kasus DM terkonsentrasi di daerah dengan jumlah penderita menengah hingga tinggi.