import sqlite3

# Fungsi untuk menginisiasi database
def inisiasi_db():
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        # Membuat tabel 'teks' jika belum ada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teks_mentah TEXT,
                teks_bersih TEXT
            )
        ''')
        conn.commit()

# Fungsi untuk menambahkan data teks mentah dan teks bersih ke dalam tabel
def tambah_data(teks_mentah, teks_bersih):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        # Menambahkan data ke dalam tabel 'teks'
        cursor.execute('INSERT INTO teks (teks_mentah, teks_bersih) VALUES (?, ?)', (teks_mentah, teks_bersih))
        conn.commit()
