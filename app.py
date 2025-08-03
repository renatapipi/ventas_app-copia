import os
import csv
from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Ruta para mostrar formulario y lista productos
@app.route('/productos', methods=['GET', 'POST'])
def productos():
    if 'usuario' not in session:
        return redirect('/')

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        costo = request.form.get('costo', '').strip()
        ganancia = request.form.get('ganancia', '').strip()
        marca = request.form.get('marca', '').strip()

        if nombre and costo and ganancia and marca:
            with open('productos.csv', 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow([nombre, costo, ganancia, marca])
        return redirect('/productos')

    return render_template('productos.html')

# API que devuelve productos en JSON
@app.route('/api/productos')
def api_productos():
    productos = []
    if os.path.exists('productos.csv'):
        with open('productos.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 4:
                    productos.append({
                        'nombre': row[0],
                        'costo': row[1],
                        'ganancia': row[2],
                        'marca': row[3]
                    })
    return jsonify(productos)

# Login muy simple para pruebas (sin seguridad real)
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        if user == 'admin' and password == '1234':
            session['usuario'] = user
            session['rol'] = 'admin'
            return redirect('/menu')
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)
@app.route('/menu')
def menu():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('index.html', usuario=session['usuario'], rol=session.get('rol'))
@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if 'usuario' not in session:
        return redirect('/')
    
    filtro_marca = request.args.get('marca', '')
    productos = []
    with open('productos.csv') as f:
        for row in csv.reader(f):
            if filtro_marca == '' or filtro_marca.lower() in row[3].lower():
                productos.append(row)

    if request.method == 'POST':
        producto = request.form['producto']
        cantidad = int(request.form['cantidad'])
        forma_pago = request.form['forma_pago']
        descuento = float(request.form['descuento'])
        recargo = float(request.form['recargo'])
        for p in productos:
            if producto == p[0]:
                costo = float(p[1])
                ganancia = float(p[2])
                total = (costo + ganancia) * cantidad
                total -= total * descuento / 100
                total += total * recargo / 100
                with open('ventas.csv', 'a', newline='') as f:
                    csv.writer(f).writerow([producto, cantidad, session['usuario'], ganancia, datetime.now().strftime('%Y-%m-%d %H:%M'), total, forma_pago])
                return render_template('recibo.html', producto=producto, cantidad=cantidad, total=round(total, 2), forma_pago=forma_pago, descuento=descuento, recargo=recargo)
    return render_template('ventas.html', productos=productos)

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)



