from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'factur_house_oro_2026'

# Carpeta para las fotos de los productos
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def conectar_db():
    conn = sqlite3.connect('factur_house_db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nombre TEXT, precio REAL, stock INTEGER, 
                       imagen TEXT, genero TEXT, categoria TEXT, 
                       promo INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    cat = request.args.get('cat')
    conn = conectar_db()
    cursor = conn.cursor()
    if cat and cat != 'Todas':
        cursor.execute("SELECT * FROM productos WHERE categoria = ? ORDER BY id DESC", (cat,))
    else:
        cursor.execute("SELECT * FROM productos ORDER BY id DESC")
    todos = cursor.fetchall()
    cursor.execute("SELECT DISTINCT categoria FROM productos")
    categorias = [row['categoria'] for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', productos=todos, categorias=categorias)

@app.route('/quienes-somos')
def historia():
    return render_template('historia.html')

@app.route('/personalizacion')
def personalizacion():
    return render_template('personalizacion.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'oro2026':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = conectar_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        genero = request.form.get('genero', 'Unisex')
        categoria = request.form.get('categoria', 'Varios')
        imagen = request.files['imagen']
        
        foto = f"{nombre.replace(' ', '_')}.jpg" if imagen else "default.jpg"
        if imagen:
            imagen.save(os.path.join(UPLOAD_FOLDER, foto))
            
        cursor.execute('''INSERT INTO productos (nombre, precio, stock, imagen, genero, categoria) 
                          VALUES (?,?,?,?,?,?)''', (nombre, precio, stock, foto, genero, categoria))
        conn.commit()
        return redirect(url_for('admin'))
    
    cursor.execute("SELECT * FROM productos ORDER BY id DESC")
    inventario = cursor.fetchall()
    conn.close()
    return render_template('admin.html', inventario=inventario)

if __name__ == '__main__':
    inicializar_db()
