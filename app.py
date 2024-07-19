from flask import Flask, request, jsonify, send_from_directory  # Import modul Flask dan beberapa fungsi terkait
from flask_swagger_ui import get_swaggerui_blueprint  # Import fungsi untuk konfigurasi Swagger UI
import os  # Import modul os untuk operasi sistem
from werkzeug.utils import secure_filename  # Import fungsi secure_filename untuk mengamankan nama file
import pandas as pd  # Import modul pandas untuk manipulasi data CSV
import sqlite3  # Import modul sqlite3 untuk bekerja dengan database SQLite
import re  # Import modul re untuk ekspresi reguler
from cleaning import cleanse_text, cleanse_file  # Import fungsi-fungsi membersihkan teks dan file dari modul cleaning
from database import inisiasi_db, tambah_data  # Import fungsi-fungsi terkait database dari modul database

app = Flask(__name__)  # Inisialisasi aplikasi Flask

# Konfigurasi Swagger UI untuk dokumentasi API
SWAGGER_URL = '/swagger'  # URL untuk Swagger UI
API_URL = '/static/swagger.json'  # URL untuk spesifikasi API dalam format JSON
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Text Cleaning API"})  # Konfigurasi blueprint Swagger UI
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)  # Registrasi blueprint Swagger UI pada aplikasi Flask dengan prefix /swagger



# Endpoint untuk membersihkan teks
@app.route('/clean_text', methods=['POST'])  # Deklarasi endpoint /clean_text dengan metode POST
def clean_text_endpoint():
    data = request.json  # Mendapatkan data JSON dari request POST
    
    raw_text = data.get('text', '')  # Mengambil teks mentah dari data, default kosong jika tidak ada
    clean_text = cleanse_text(raw_text)  # Membersihkan teks mentah menggunakan fungsi cleanse_text
    tambah_data(raw_text, clean_text)  # Menyimpan teks mentah dan teks bersih ke database
    
    return jsonify({'clean_text': clean_text})  # Mengembalikan teks bersih dalam format JSON

# Endpoint untuk membersihkan file CSV
@app.route('/clean_csv', methods=['POST'])  # Deklarasi endpoint /clean_csv dengan metode POST
def clean_csv_endpoint():
    file = request.files['file']  # Mendapatkan file dari request POST
    column_name = request.form.get('column_name', 'Tweet')  # Mendapatkan nama kolom dari form data, default 'Tweet' jika tidak ada
    
    if file.filename == '':  # Memeriksa jika tidak ada file yang dipilih
        return jsonify({'error': 'No file selected'}), 400  # Mengembalikan pesan error jika tidak ada file dipilih
    
    # Simpan file ke direktori 'uploads'
    filepath = os.path.join('uploads', secure_filename(file.filename))  # Mengamankan dan menentukan path untuk menyimpan file
    file.save(filepath)  # Menyimpan file ke path yang ditentukan
    
    # Bersihkan file CSV dan simpan file bersih ke direktori 'uploads'
    cleaned_df = cleanse_file(filepath, column_name)  # Membersihkan file CSV
    if cleaned_df is None:  # Memeriksa jika gagal membersihkan file
        return jsonify({'error': 'Failed to clean CSV file'}), 500  # Mengembalikan pesan error jika gagal membersihkan file
    
    cleaned_filepath = os.path.join('uploads', 'cleaned_' + secure_filename(file.filename))  # Path untuk menyimpan file CSV bersih
    cleaned_df.to_csv(cleaned_filepath, index=False)  # Menyimpan DataFrame yang bersih ke CSV
    
    # Optional: tambahkan data mentah dan bersih ke database
    if column_name in cleaned_df.columns and 'cleaned_text' in cleaned_df.columns:  # Memeriksa keberadaan kolom yang diperlukan
        for raw_text, clean_text in zip(cleaned_df[column_name], cleaned_df['cleaned_text']):  # Loop untuk tambahkan data ke database
            tambah_data(raw_text, clean_text)
    
    return jsonify({'message': 'CSV file cleaned successfully', 'cleaned_filepath': cleaned_filepath})  # Mengembalikan pesan sukses dan path file CSV bersih

# Endpoint untuk mengunggah dan membersihkan file CSV
@app.route('/upload_csv', methods=['POST'])  # Deklarasi endpoint /upload_csv dengan metode POST
def upload_csv():
    file = request.files['file']  # Mendapatkan file dari request POST
    column_name = request.form.get('column_name', 'Tweet')  # Mendapatkan nama kolom dari form data, default 'Tweet' jika tidak ada

    if file.filename == '':  # Memeriksa jika tidak ada file yang dipilih
        return jsonify({'error': 'No file selected'}), 400  # Mengembalikan pesan error jika tidak ada file dipilih
    
    # Simpan file ke direktori 'uploads'
    filepath = os.path.join('uploads', secure_filename(file.filename))  # Mengamankan dan menentukan path untuk menyimpan file
    file.save(filepath)  # Menyimpan file ke path yang ditentukan
    
    # Bersihkan file CSV dan simpan file bersih ke direktori 'uploads'
    cleaned_df = cleanse_file(filepath, column_name)  # Membersihkan file CSV
    if cleaned_df is None:  # Memeriksa jika gagal membersihkan file
        return jsonify({'error': 'Failed to clean CSV file'}), 500  # Mengembalikan pesan error jika gagal membersihkan file
    
    cleaned_filepath = os.path.join('uploads', 'cleaned_' + secure_filename(file.filename))  # Path untuk menyimpan file CSV bersih
    cleaned_df.to_csv(cleaned_filepath, index=False)  # Menyimpan DataFrame yang bersih ke CSV
    
    # Optional: tambahkan data mentah dan bersih ke database
    if column_name in cleaned_df.columns and 'cleaned_text' in cleaned_df.columns:  # Memeriksa keberadaan kolom yang diperlukan
        for raw_text, clean_text in zip(cleaned_df[column_name], cleaned_df['cleaned_text']):  # Loop untuk tambahkan data ke database
            tambah_data(raw_text, clean_text)
    
    return jsonify({'message': 'CSV file uploaded and cleaned successfully', 'cleaned_filepath': cleaned_filepath})  # Mengembalikan pesan sukses dan path file CSV bersih


if __name__ == '__main__':
    inisiasi_db()  # Inisiasi database saat pertama kali menjalankan aplikasi
    if not os.path.exists('uploads'):  # Memeriksa keberadaan direktori 'uploads'
        os.makedirs('uploads')  # Membuat direktori 'uploads' jika belum ada
    app.run(debug=True)  # Menjalankan aplikasi Flask dalam mode debug
