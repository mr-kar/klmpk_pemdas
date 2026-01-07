from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import matplotlib 
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

app = Flask(__name__)
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS data_dm_input (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kabupaten TEXT,
            tahun INTEGER,
            jumlah_penderita INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

def import_csv_to_db():
    conn = get_db_connection()

    # cek apakah tabel sudah ada isinya
    cek = conn.execute("SELECT COUNT(*) FROM data_dm_input").fetchone()[0]

    if cek == 0:
        df_csv = pd.read_csv("dinkes-od_17448_jml_penderita_diabetes_melitus_brdsrkn_kabupatenko_v2_data.csv")

        for _, row in df_csv.iterrows():
            conn.execute(
                """
                INSERT INTO data_dm_input (nama_kabupaten, tahun, jumlah_penderita)
                VALUES (?, ?, ?)
                """,
                (
                    row["nama_kabupaten_kota"],
                    int(row["tahun"]),
                    int(row["jumlah_penderita_dm"])
                )
            )

        conn.commit()

    conn.close()

import_csv_to_db()
# Load data
df = pd.read_csv("dinkes-od_17448_jml_penderita_diabetes_melitus_brdsrkn_kabupatenko_v2_data.csv")

@app.route("/")
def beranda():
    return render_template("index.html")

@app.route("/crud", methods=["GET", "POST"])
def crud():
    conn = get_db_connection()

    if request.method == "POST":
        nama = request.form["nama_kabupaten"]
        tahun = request.form["tahun"]
        jumlah = request.form["jumlah_penderita"]

        conn.execute(
            "INSERT INTO data_dm_input (nama_kabupaten, tahun, jumlah_penderita) VALUES (?, ?, ?)",
            (nama, tahun, jumlah)
        )
        conn.commit()

    data = conn.execute(
        "SELECT * FROM data_dm_input"
    ).fetchall()

    conn.close()
    return render_template("crud.html", data=data)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()

    if request.method == "POST":
        nama = request.form["nama_kabupaten"]
        tahun = request.form["tahun"]
        jumlah = request.form["jumlah_penderita"]

        conn.execute(
            "UPDATE data_dm_input SET nama_kabupaten=?, tahun=?, jumlah_penderita=? WHERE id=?",
            (nama, tahun, jumlah, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("crud"))

    data = conn.execute(
        "SELECT * FROM data_dm_input WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()
    return render_template("crud.html", edit_data=data)

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM data_dm_input WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("crud"))

@app.route("/soal-ac")
def soal_ac():

    # =====================
    # A. Pengenalan Data
    # =====================
    head = df.head().to_html(index=False)
    tail = df.tail().to_html(index=False)

    buffer = StringIO()
    df.info(buf=buffer)
    info_df = buffer.getvalue().replace("\n", "<br>")


    describe = df.describe().to_html()

    tahun_unik = df["tahun"].unique()
    kab_unik = df["nama_kabupaten_kota"].unique()
    jumlah_kab = len(kab_unik)

    kolom_tertentu = df[[
        "nama_kabupaten_kota",
        "jumlah_penderita_dm",
        "tahun"
    ]].to_html(index=False)

    # =====================
    # B. Filtering & Sorting
    # =====================
    data_2019 = df[df["tahun"] == 2019].to_html(index=False)

    dm_100k = df[df["jumlah_penderita_dm"] > 100000].to_html(index=False)

    sort_dm = df.sort_values(
        by="jumlah_penderita_dm",
        ascending=False
    ).to_html(index=False)

    sort_tahun_dm = df.sort_values(
        by=["tahun", "jumlah_penderita_dm"],
        ascending=[True, False]
    ).to_html(index=False)

    top10_2019 = (
        df[df["tahun"] == 2019]
        .sort_values(by="jumlah_penderita_dm", ascending=False)
        .head(10)
        .to_html(index=False)
    )

    bogor = df[
        df["nama_kabupaten_kota"] == "KABUPATEN BOGOR"
    ].to_html(index=False)

    # =====================
    # C. Agregasi & Transformasi
    # =====================
    total_per_tahun = (
        df.groupby("tahun")["jumlah_penderita_dm"]
        .sum()
        .reset_index()
        .to_html(index=False)
    )

    rata_kab = (
        df.groupby("nama_kabupaten_kota")["jumlah_penderita_dm"]
        .mean()
        .reset_index()
        .to_html(index=False)
    )

    total_kab = (
        df.groupby("nama_kabupaten_kota")["jumlah_penderita_dm"]
        .sum()
    )

    kab_tertinggi = total_kab.idxmax()
    kab_terendah = total_kab.idxmin()

    # Kategori DM
    df_kategori = df.copy()
    df_kategori["kategori_dm"] = np.where(
        df_kategori["jumlah_penderita_dm"] < 50000, "Rendah",
        np.where(df_kategori["jumlah_penderita_dm"] < 100000, "Sedang", "Tinggi")
    )

    kategori_table = df_kategori.to_html(index=False)

    # Persentase per tahun
    df_persen = df.copy()
    df_persen["persentase_tahun"] = (
        df_persen["jumlah_penderita_dm"] /
        df_persen.groupby("tahun")["jumlah_penderita_dm"].transform("sum")
    ) * 100

    persen_table = df_persen.to_html(index=False)

    ringkasan = (
        df.groupby("tahun")
        .agg(
            total_jumlah_penderita_dm=("jumlah_penderita_dm", "sum"),
            jumlah_kabupaten_kota=("nama_kabupaten_kota", "nunique")
        )
        .reset_index()
        .to_html(index=False)
    )

    return render_template(
        "soal_ac.html",
        head=head,
        tail=tail,
        info_df=info_df,
        describe=describe,
        tahun_unik=tahun_unik,
        kab_unik=kab_unik,
        jumlah_kab=jumlah_kab,
        kolom_tertentu=kolom_tertentu,
        data_2019=data_2019,
        dm_100k=dm_100k,
        sort_dm=sort_dm,
        sort_tahun_dm=sort_tahun_dm,
        top10_2019=top10_2019,
        bogor=bogor,
        total_per_tahun=total_per_tahun,
        rata_kab=rata_kab,
        kab_tertinggi=kab_tertinggi,
        kab_terendah=kab_terendah,
        kategori_table=kategori_table,
        persen_table=persen_table,
        ringkasan=ringkasan
    )

@app.route("/soal-d")
def soal_d():

    df_local = df.copy()

    # =====================
    # SOAL 20
    # Bar chart kab/kota 2019
    # =====================
    df_2019 = df_local[df_local["tahun"] == 2019]

    plt.figure(figsize=(10, 6))
    plt.bar(df_2019["nama_kabupaten_kota"], df_2019["jumlah_penderita_dm"])
    plt.xticks(rotation=90)
    plt.xlabel("Kabupaten/Kota")
    plt.ylabel("Jumlah Penderita DM")
    plt.title("Jumlah Penderita DM per Kabupaten/Kota (2019)")
    plt.tight_layout()
    plt.savefig("static/images/bar_2019.png")
    plt.close()

    # =====================
    # SOAL 21
    # Line chart total per tahun
    # =====================
    total_per_tahun = (
        df_local.groupby("tahun")["jumlah_penderita_dm"]
        .sum()
    )

    plt.figure()
    plt.plot(
        total_per_tahun.index,
        total_per_tahun.values,
        marker="o"
    )
    plt.xlabel("Tahun")
    plt.ylabel("Total Penderita DM")
    plt.title("Total Penderita DM Jawa Barat per Tahun")
    plt.tight_layout()
    plt.savefig("static/images/line_total_tahun.png")
    plt.close()

    # =====================
    # SOAL 22
    # Bar horizontal top 10 2019
    # =====================
    top10 = df_2019.sort_values(
        by="jumlah_penderita_dm",
        ascending=False
    ).head(10)

    plt.figure()
    plt.barh(
        top10["nama_kabupaten_kota"],
        top10["jumlah_penderita_dm"]
    )
    plt.xlabel("Jumlah Penderita DM")
    plt.ylabel("Kabupaten/Kota")
    plt.title("Top 10 Kabupaten/Kota Penderita DM Tertinggi (2019)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("static/images/top10_2019.png")
    plt.close()

    # =====================
    # SOAL 23
    # Pie chart kategori DM 2019
    # =====================
    df_2019["kategori_dm"] = df_2019["jumlah_penderita_dm"].apply(
        lambda x: "Rendah" if x < 50000 else
        "Sedang" if x < 100000 else "Tinggi"
    )

    kategori_sum = (
        df_2019.groupby("kategori_dm")["jumlah_penderita_dm"]
        .sum()
    )

    plt.figure()
    plt.pie(
        kategori_sum,
        labels=kategori_sum.index,
        autopct="%1.1f%%"
    )
    plt.title("Proporsi Penderita DM berdasarkan Kategori (2019)")
    plt.tight_layout()
    plt.savefig("static/images/pie_kategori_2019.png")
    plt.close()

    # =====================
    # SOAL 24
    # Bar chart 3 tahun terakhir
    # =====================
    tahun_terakhir = sorted(df_local["tahun"].unique())[-3:]

    total_3tahun = (
        df_local[df_local["tahun"].isin(tahun_terakhir)]
        .groupby("tahun")["jumlah_penderita_dm"]
        .sum()
    )

    plt.figure()
    plt.bar(total_3tahun.index, total_3tahun.values)
    plt.xlabel("Tahun")
    plt.ylabel("Total Penderita DM")
    plt.title("Perbandingan Total Penderita DM (3 Tahun Terakhir)")
    plt.tight_layout()
    plt.savefig("static/images/bar_3tahun.png")
    plt.close()

    return render_template("soal_d.html")

if __name__ == "__main__":
    app.run(debug=True)


