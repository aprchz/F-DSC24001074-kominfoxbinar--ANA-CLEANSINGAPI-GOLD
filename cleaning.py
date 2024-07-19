import pandas as pd  # Mengimpor pustaka pandas untuk manipulasi data
import re  # Mengimpor pustaka re untuk operasi regex

# Membaca kamus alay dan kata kasar dari file CSV
alay_dict = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)  # Membaca file CSV kamus alay dengan encoding latin-1 dan tanpa header
abusive_dict = pd.read_csv('abusive.csv', encoding='latin-1')  # Membaca file CSV kamus kata kasar dengan encoding latin-1

alay_dict_map = dict(zip(alay_dict[0], alay_dict[1]))  # Membuat peta dari kamus alay dengan pasangan kata asal dan kata normalisasi

abusive_dict_map = {}  # Inisialisasi kamus kata kasar kosong
expected_column = 'ABUSIVE'  # Nama kolom yang diharapkan ada di file abusive.csv

# Mengecek apakah kolom 'ABUSIVE' ada di file abusive.csv
if expected_column in abusive_dict.columns:  # Jika kolom 'ABUSIVE' ada
    abusive_dict_map = dict(zip(abusive_dict[expected_column], [None] * len(abusive_dict)))  # Membuat peta dari kamus kata kasar
else:  # Jika kolom 'ABUSIVE' tidak ada
    print(f"Peringatan: Kolom '{expected_column}' tidak ditemukan di abusive.csv. Menggunakan pemetaan default.")  # Menampilkan peringatan
    abusive_dict_map = {}  # Menggunakan kamus kosong

# Fungsi untuk mengubah teks menjadi huruf kecil
def lowercase(text):
    return text.lower()  # Mengubah teks menjadi huruf kecil

# Fungsi untuk menghapus karakter yang tidak diperlukan
def remove_unnecessary_char(text):
    text = re.sub(r'\\+n', ' ', text)  # Menghapus karakter "\n" yang berlebihan
    text = re.sub(r'\n', ' ', text)  # Menghapus karakter newline
    text = re.sub(r'\brt\b', ' ', text, flags=re.IGNORECASE)  # Menghapus kata "rt" (retweet)
    text = re.sub(r'\buser\b', ' ', text, flags=re.IGNORECASE)  # Menghapus kata "user"
    text = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))', ' ', text)  # Menghapus URL
    text = re.sub(r'[:,;\\+]', ' ', text)  # Menghapus beberapa tanda baca
    text = re.sub(r'  +', ' ', text)  # Menghapus spasi berlebih
    return text  # Mengembalikan teks yang telah dibersihkan

# Fungsi untuk menghapus karakter non-alfanumerik
def remove_non_alphanumeric(text):
    text = re.sub(r'[^0-9a-zA-Z\s]+', ' ', text)  # Menghapus karakter non-alfanumerik
    return text  # Mengembalikan teks yang telah dibersihkan

# Fungsi untuk menormalisasi kata alay
def normalize_alay(text):
    return ' '.join([alay_dict_map.get(word, word) for word in text.split()])  # Menormalisasi kata alay dalam teks

# Fungsi untuk menghapus byte emotikon
def remove_emoticon_byte(text):
    text = text.replace("\\", " ")  # Mengganti karakter backslash dengan spasi
    text = re.sub(r'x..', ' ', text)  # Menghapus byte emotikon
    text = re.sub(r' n ', ' ', text)  # Menghapus karakter " n "
    text = re.sub(r'  +', ' ', text)  # Menghapus spasi berlebih
    return text  # Mengembalikan teks yang telah dibersihkan

# Fungsi untuk menghapus spasi di awal teks
def remove_early_space(text):
    if text and text[0] == ' ':  # Jika teks diawali dengan spasi
        return text[1:]  # Menghapus spasi di awal teks
    return text  # Mengembalikan teks

# Fungsi utama untuk membersihkan teks
def cleanse_text(text):
    text = lowercase(text)  # Mengubah teks menjadi huruf kecil
    text = remove_non_alphanumeric(text)  # Menghapus karakter non-alfanumerik
    text = remove_unnecessary_char(text)  # Menghapus karakter yang tidak diperlukan
    
    words = []  # Inisialisasi daftar untuk menampung kata yang telah dibersihkan
    for word in text.split():  # Untuk setiap kata dalam teks
        cleaned_word = alay_dict_map.get(word, word)  # Menormalisasi kata alay
        
        if cleaned_word.lower() in abusive_dict_map:  # Jika kata terdapat dalam kamus kata kasar
            cleaned_word = abusive_dict_map[cleaned_word.lower()]  # Menghapus kata kasar
        
        if isinstance(cleaned_word, str) and cleaned_word.strip():  # Jika kata valid (bukan None atau spasi)
            words.append(cleaned_word)  # Menambahkan kata yang sudah dibersihkan
    
    text = ' '.join(words)  # Menggabungkan kata-kata yang telah dibersihkan menjadi satu teks
    text = remove_emoticon_byte(text)  # Menghapus byte emotikon
    text = remove_early_space(text)  # Menghapus spasi di awal teks
    
    return text  # Mengembalikan teks yang telah dibersihkan

# Fungsi untuk membersihkan file CSV
def cleanse_file(filepath, column_name):
    try:
        # Membaca CSV dengan encoding latin-1
        df = pd.read_csv(filepath, encoding='latin-1')  # Membaca file CSV dengan encoding latin-1
    except Exception as e:  # Jika terjadi kesalahan
        print(f"Error reading CSV file: {e}")  # Menampilkan pesan kesalahan
        return None  # Mengembalikan None
    
    # Cek bila ada kolom seperti itu
    if column_name in df.columns:  # Jika kolom yang dimaksud ada
        df['cleaned_text'] = df[column_name].apply(cleanse_text)  # Menerapkan fungsi cleanse_text pada kolom yang dimaksud
    else:  # Jika kolom yang dimaksud tidak ada
        print(f"Column '{column_name}' not found in the DataFrame.")  # Menampilkan pesan kesalahan
        return None  # Mengembalikan None
    
    return df  # Mengembalikan DataFrame yang telah dibersihkan
