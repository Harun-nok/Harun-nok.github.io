import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Veritabanı bağlantısı
def get_db_connection():
    conn = sqlite3.connect('muhasebe.db')
    conn.row_factory = sqlite3.Row  # Verileri sözlük şeklinde almak için
    return conn

# Veritabanı tablo oluşturma (ilk çalıştırmada)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sales tablosunu oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sales (
            id INTEGER PRIMARY KEY,
            aptavoycu_name TEXT,
            doner_coreki_180q INTEGER DEFAULT 0,
            corek_600q INTEGER DEFAULT 0,
            corek_750q INTEGER DEFAULT 0,
            corek_800q INTEGER DEFAULT 0,
            corek_1kg INTEGER DEFAULT 0,
            expected_income REAL DEFAULT 0,
            is_settled BOOLEAN DEFAULT 0
        )
    ''')

    # DailyProduction tablosunu oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DailyProduction (
            id INTEGER PRIMARY KEY,
            date TEXT,
            corek_600q INTEGER DEFAULT 0,
            corek_750q INTEGER DEFAULT 0,
            corek_800q INTEGER DEFAULT 0,
            corek_1kg INTEGER DEFAULT 0,
            expected_income REAL DEFAULT 0
        )
    ''')

    # PencereSales tablosunu oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PencereSales (
            id INTEGER PRIMARY KEY,
            corek_600q INTEGER DEFAULT 0,
            corek_750q INTEGER DEFAULT 0,
            corek_800q INTEGER DEFAULT 0,
            corek_1kg INTEGER DEFAULT 0,
            yanan2 INTEGER DEFAULT 0,
            kut2 INTEGER DEFAULT 0,
            bos_mesoklar INTEGER DEFAULT 0,
            isci_corek_600q INTEGER DEFAULT 0,
            isci_corek_750q INTEGER DEFAULT 0,
            isci_corek_800q INTEGER DEFAULT 0,
            isci_corek_1kg INTEGER DEFAULT 0,
            vazvrat_corek_600q INTEGER DEFAULT 0,
            vazvrat_corek_750q INTEGER DEFAULT 0,
            vazvrat_corek_800q INTEGER DEFAULT 0,
            vazvrat_corek_1kg INTEGER DEFAULT 0,
            total_income REAL DEFAULT 0
        )
    ''')

    # LostProduction tablosunu oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LostProduction (
            id INTEGER PRIMARY KEY,
            yanan_600q INTEGER DEFAULT 0,
            yanan_750q INTEGER DEFAULT 0,
            yanan_800q INTEGER DEFAULT 0,
            yanan_1kg INTEGER DEFAULT 0,
            kut_600q INTEGER DEFAULT 0,
            kut_750q INTEGER DEFAULT 0,
            kut_800q INTEGER DEFAULT 0,
            kut_1kg INTEGER DEFAULT 0,
            yiyilen_600q INTEGER DEFAULT 0,
            yiyilen_750q INTEGER DEFAULT 0,
            yiyilen_800q INTEGER DEFAULT 0,
            yiyilen_1kg INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# Günlük üretim ekleme/güncelleme işlevi
@app.route('/update_production', methods=['POST'])
def update_production():
    corek_600q = int(request.form.get('corek_600q', 0))
    corek_750q = int(request.form.get('corek_750q', 0))
    corek_800q = int(request.form.get('corek_800q', 0))
    corek_1kg = int(request.form.get('corek_1kg', 0))

    # Fiyatları belirle
    expected_income = (corek_600q * 0.60) + (corek_750q * 0.70) + \
                      (corek_800q * 0.80) + (corek_1kg * 1.00)

    today = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Günlük üretimi ekle veya güncelle
    cursor.execute('''
        INSERT OR REPLACE INTO DailyProduction (
            id, date, corek_600q, corek_750q, corek_800q, corek_1kg, expected_income
        ) VALUES (1, ?, ?, ?, ?, ?, ?)
    ''', (today, corek_600q, corek_750q, corek_800q, corek_1kg, expected_income))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Eksilen çörek ekleme işlevi
@app.route('/add_lost_production', methods=['POST'])
def add_lost_production():
    yanan_600q = int(request.form.get('yanan_600q', 0))
    yanan_750q = int(request.form.get('yanan_750q', 0))
    yanan_800q = int(request.form.get('yanan_800q', 0))
    yanan_1kg = int(request.form.get('yanan_1kg', 0))
    kut_600q = int(request.form.get('kut_600q', 0))
    kut_750q = int(request.form.get('kut_750q', 0))
    kut_800q = int(request.form.get('kut_800q', 0))
    kut_1kg = int(request.form.get('kut_1kg', 0))
    yiyilen_600q = int(request.form.get('yiyilen_600q', 0))
    yiyilen_750q = int(request.form.get('yiyilen_750q', 0))
    yiyilen_800q = int(request.form.get('yiyilen_800q', 0))
    yiyilen_1kg = int(request.form.get('yiyilen_1kg', 0))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Eksilen çörekleri güncelle
    cursor.execute('''
        INSERT OR REPLACE INTO LostProduction (
            id, yanan_600q, yanan_750q, yanan_800q, yanan_1kg,
            kut_600q, kut_750q, kut_800q, kut_1kg,
            yiyilen_600q, yiyilen_750q, yiyilen_800q, yiyilen_1kg
        ) VALUES (
            1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    ''', (
        yanan_600q, yanan_750q, yanan_800q, yanan_1kg,
        kut_600q, kut_750q, kut_800q, kut_1kg,
        yiyilen_600q, yiyilen_750q, yiyilen_800q, yiyilen_1kg
    ))

    # Günlük üretimden eksilen çörekleri düş
    cursor.execute('''
        UPDATE DailyProduction
        SET
            corek_600q = corek_600q - ? - ? - ?,
            corek_750q = corek_750q - ? - ? - ?,
            corek_800q = corek_800q - ? - ? - ?,
            corek_1kg = corek_1kg - ? - ? - ?
        WHERE id = 1
    ''', (
        yanan_600q, kut_600q, yiyilen_600q,
        yanan_750q, kut_750q, yiyilen_750q,
        yanan_800q, kut_800q, yiyilen_800q,
        yanan_1kg, kut_1kg, yiyilen_1kg
    ))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Satış ekleme işlevi
@app.route('/add_sale', methods=['POST'])
def add_sale():
    aptavoycu_name = request.form['aptavoycu_name']
    doner_coreki_180q = int(request.form.get('doner_coreki_180q', 0))
    corek_600q = int(request.form.get('corek_600q', 0))
    corek_750q = int(request.form.get('corek_750q', 0))
    corek_800q = int(request.form.get('corek_800q', 0))
    corek_1kg = int(request.form.get('corek_1kg', 0))

    # Gelmesi gereken para hesaplaması
    expected_income = (
        (doner_coreki_180q * 0.3) +
        (corek_600q * 0.4) +
        (corek_750q * 0.52) +
        (corek_800q * 0.7) +
        (corek_1kg * 0.9)
    )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Satış bilgilerini ekle
    cursor.execute('''
        INSERT INTO Sales (
            aptavoycu_name, doner_coreki_180q, corek_600q, corek_750q,
            corek_800q, corek_1kg, expected_income
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        aptavoycu_name, doner_coreki_180q, corek_600q, corek_750q,
        corek_800q, corek_1kg, expected_income
    ))

    # Günlük üretimden çörekleri eksilt
    cursor.execute('''
        UPDATE DailyProduction
        SET
            corek_600q = corek_600q - ?,
            corek_750q = corek_750q - ?,
            corek_800q = corek_800q - ?,
            corek_1kg = corek_1kg - ?
        WHERE id = 1
    ''', (corek_600q, corek_750q, corek_800q, corek_1kg))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Ucuz Mallar ve Pencere Satışlarını Ekleme
@app.route('/add_discounted_and_pencere_sales', methods=['POST'])
def add_discounted_and_pencere_sales():
    # Ucuz mallar ve pencere satışları için alınan veriler
    corek_600q = int(request.form.get('corek_600q', 0))
    corek_750q = int(request.form.get('corek_750q', 0))
    corek_800q = int(request.form.get('corek_800q', 0))
    corek_1kg = int(request.form.get('corek_1kg', 0))
    yanan2 = int(request.form.get('yanan2', 0))
    kut2 = int(request.form.get('kut2', 0))
    bos_mesoklar = int(request.form.get('bos_mesoklar', 0))

    isci_coreyi = {
        'corek_600q': int(request.form.get('isci_corek_600q', 0)),
        'corek_750q': int(request.form.get('isci_corek_750q', 0)),
        'corek_800q': int(request.form.get('isci_corek_800q', 0)),
        'corek_1kg': int(request.form.get('isci_corek_1kg', 0)),
    }

    vazvrat_coreyi = {
        'corek_600q': int(request.form.get('vazvrat_corek_600q', 0)),
        'corek_750q': int(request.form.get('vazvrat_corek_750q', 0)),
        'corek_800q': int(request.form.get('vazvrat_corek_800q', 0)),
        'corek_1kg': int(request.form.get('vazvrat_corek_1kg', 0)),
    }

    # Fiyatları belirle
    total_income = (
        (corek_600q * 0.60) + (corek_750q * 0.70) +
        (corek_800q * 0.80) + (corek_1kg * 1.00) +
        (yanan2 * 0.20) + (kut2 * 0.20) + (bos_mesoklar * 0.20) +
        (isci_coreyi['corek_600q'] * 0.40) + (isci_coreyi['corek_750q'] * 0.52) +
        (isci_coreyi['corek_800q'] * 0.70) + (isci_coreyi['corek_1kg'] * 0.75) +
        (vazvrat_coreyi['corek_600q'] * 0.30) + (vazvrat_coreyi['corek_750q'] * 0.35) +
        (vazvrat_coreyi['corek_800q'] * 0.40) + (vazvrat_coreyi['corek_1kg'] * 0.50)
    )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Pencere satışlarını ekle veya güncelle
    cursor.execute('''
        INSERT OR REPLACE INTO PencereSales (
            id, corek_600q, corek_750q, corek_800q, corek_1kg,
            yanan2, kut2, bos_mesoklar, isci_corek_600q, isci_corek_750q,
            isci_corek_800q, isci_corek_1kg, vazvrat_corek_600q,
            vazvrat_corek_750q, vazvrat_corek_800q, vazvrat_corek_1kg, total_income
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        1, corek_600q, corek_750q, corek_800q, corek_1kg,
        yanan2, kut2, bos_mesoklar,
        isci_coreyi['corek_600q'], isci_coreyi['corek_750q'],
        isci_coreyi['corek_800q'], isci_coreyi['corek_1kg'],
        vazvrat_coreyi['corek_600q'], vazvrat_coreyi['corek_750q'],
        vazvrat_coreyi['corek_800q'], vazvrat_coreyi['corek_1kg'],
        total_income
    ))

    # Günlük üretimden çörekleri eksilt
    cursor.execute('''
        UPDATE DailyProduction
        SET
            corek_600q = corek_600q - ? - ? - ?,
            corek_750q = corek_750q - ? - ? - ?,
            corek_800q = corek_800q - ? - ? - ?,
            corek_1kg = corek_1kg - ? - ? - ?
        WHERE id = 1
    ''', (
        corek_600q, isci_coreyi['corek_600q'], vazvrat_coreyi['corek_600q'],
        corek_750q, isci_coreyi['corek_750q'], vazvrat_coreyi['corek_750q'],
        corek_800q, isci_coreyi['corek_800q'], vazvrat_coreyi['corek_800q'],
        corek_1kg, isci_coreyi['corek_1kg'], vazvrat_coreyi['corek_1kg']
    ))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Pencere satışını sıfırlama işlevi
@app.route('/reset_pencere_sales', methods=['POST'])
def reset_pencere_sales():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Pencere satışlarını sıfırla
    cursor.execute('''
        UPDATE PencereSales 
        SET 
            corek_600q = 0,
            corek_750q = 0,
            corek_800q = 0,
            corek_1kg = 0,
            yanan2 = 0,
            kut2 = 0,
            bos_mesoklar = 0,
            isci_corek_600q = 0,
            isci_corek_750q = 0,
            isci_corek_800q = 0,
            isci_corek_1kg = 0,
            vazvrat_corek_600q = 0,
            vazvrat_corek_750q = 0,
            vazvrat_corek_800q = 0,
            vazvrat_corek_1kg = 0,
            total_income = 0
        WHERE id = 1
    ''')

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Günlük üretimi sıfırlama işlevi
@app.route('/reset_production', methods=['POST'])
def reset_production():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Günlük üretimi sıfırla
    cursor.execute('''
        UPDATE DailyProduction 
        SET 
            corek_600q = 0,
            corek_750q = 0,
            corek_800q = 0,
            corek_1kg = 0,
            expected_income = 0
        WHERE id = 1
    ''')

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Satışları sıfırlama işlevi
@app.route('/reset_sales', methods=['POST'])
def reset_sales():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Satışları sil
    cursor.execute("DELETE FROM Sales")

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Tüm verileri sıfırlama işlevi
@app.route('/reset_all', methods=['POST'])
def reset_all():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tüm tabloları sıfırla
    cursor.execute("DELETE FROM Sales")
    cursor.execute("DELETE FROM DailyProduction")
    cursor.execute("DELETE FROM PencereSales")
    cursor.execute("DELETE FROM LostProduction")

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Satışları, günlük üretimi, pencere satışlarını getirme işlevi
def get_sales_and_production():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Satış bilgilerini al
    cursor.execute("SELECT * FROM Sales")
    sales = cursor.fetchall()

    # Günlük üretim bilgilerini al
    cursor.execute("SELECT * FROM DailyProduction WHERE id = 1")
    production = cursor.fetchone()

    # Pencere satış bilgilerini al
    cursor.execute("SELECT * FROM PencereSales WHERE id = 1")
    pencere_sales = cursor.fetchone()

    # Eksilen çörek bilgilerini al
    cursor.execute("SELECT * FROM LostProduction WHERE id = 1")
    lost_production = cursor.fetchone()

    # Eğer pencere_sales veya lost_production verisi yoksa, varsayılan değerler atıyoruz
    if not pencere_sales:
        pencere_sales = {
            'corek_600q': 0, 'corek_750q': 0, 'corek_800q': 0, 'corek_1kg': 0,
            'yanan2': 0, 'kut2': 0, 'bos_mesoklar': 0,
            'isci_corek_600q': 0, 'isci_corek_750q': 0,
            'isci_corek_800q': 0, 'isci_corek_1kg': 0,
            'vazvrat_corek_600q': 0, 'vazvrat_corek_750q': 0,
            'vazvrat_corek_800q': 0, 'vazvrat_corek_1kg': 0,
            'total_income': 0
        }

    if not lost_production:
        lost_production = {
            'yanan_600q': 0, 'yanan_750q': 0, 'yanan_800q': 0, 'yanan_1kg': 0,
            'kut_600q': 0, 'kut_750q': 0, 'kut_800q': 0, 'kut_1kg': 0,
            'yiyilen_600q': 0, 'yiyilen_750q': 0, 'yiyilen_800q': 0, 'yiyilen_1kg': 0
        }

    conn.close()
    return sales, production, pencere_sales, lost_production

# Ana sayfa (formlar, satışlar, günlük üretim ve pencere satışları için)
@app.route('/')
def index():
    sales, production, pencere_sales, lost_production = get_sales_and_production()
    return render_template(
        'index.html',
        sales=sales,
        production=production,
        pencere_sales=pencere_sales,
        lost_production=lost_production
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)