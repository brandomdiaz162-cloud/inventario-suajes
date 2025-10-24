from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
db = SQLAlchemy(app)

# --- MODELO DE DATOS ---
class Suaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suaje = db.Column(db.String(50))          # # SUAJE
    mag_sol = db.Column(db.String(50))        # MAG/SOL
    medida = db.Column(db.String(50))         # Medida
    eje = db.Column(db.String(50))            # EJE
    des = db.Column(db.String(50))            # DES
    dt = db.Column(db.String(50))             # DT
    cab_eje = db.Column(db.String(50))        # CAB EJE
    cab_des = db.Column(db.String(50))        # CAB DES
    sep_eje = db.Column(db.String(50))        # SEP EJE
    sep_des = db.Column(db.String(50))        # SEP DES
    aprox = db.Column(db.String(50))          # APROX
    forma = db.Column(db.String(50))          # FORMA
    tipo_corte = db.Column(db.String(50))     # TIPO CORTE
    radio = db.Column(db.String(50))          # RADIO
    etiqueta = db.Column(db.String(200))      # ETIQUETA
    observacion = db.Column(db.String(200))   # OBSERVACIÓN

# Crear base de datos (si no existe)
with app.app_context():
    db.create_all()

# --- RUTA PRINCIPAL (CON FILTROS) ---
@app.route('/')
def index():
    num_suaje = request.args.get('num_suaje', '').strip()
    medida = request.args.get('medida', '').strip()

    query = Suaje.query

    if num_suaje:
        query = query.filter(Suaje.suaje.like(f"%{num_suaje}%"))
    if medida:
        query = query.filter(Suaje.medida.like(f"%{medida}%"))

    suajes = query.all()
    return render_template('index.html', suajes=suajes, num_suaje=num_suaje, medida=medida)

# --- FORMULARIO NUEVO ---
@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        nuevo_suaje = Suaje(
            suaje=request.form['suaje'],
            mag_sol=request.form['mag_sol'],
            medida=request.form['medida'],
            eje=request.form['eje'],
            des=request.form['des'],
            dt=request.form['dt'],
            cab_eje=request.form['cab_eje'],
            cab_des=request.form['cab_des'],
            sep_eje=request.form['sep_eje'],
            sep_des=request.form['sep_des'],
            aprox=request.form['aprox'],
            forma=request.form['forma'],
            tipo_corte=request.form['tipo_corte'],
            radio=request.form['radio'],
            etiqueta=request.form['etiqueta'],
            observacion=request.form['observacion']
        )

        db.session.add(nuevo_suaje)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html')

# --- IMPORTAR DESDE EXCEL ---
@app.route('/importar', methods=['GET', 'POST'])
def importar():
    if request.method == 'POST':
        archivo = request.files['archivo']

        if not archivo:
            return "No se subió ningún archivo", 400

        # Guardar el archivo temporalmente
        archivo.save('importar.xlsx')

        try:
            # Leer el Excel
            df = pd.read_excel('importar.xlsx')

            # Normalizar encabezados
            df.columns = (
                df.columns.astype(str)
                .str.replace("\n", " ", regex=True)
                .str.replace('"', "", regex=False)
                .str.strip()
                .str.upper()
            )

            print("🧾 Columnas detectadas:", list(df.columns))

            # Validar columnas requeridas
            columnas_requeridas = [
                "# SUAJE", "MAG/SOL", "MEDIDA", "EJE", "DES", "DT",
                "CAB EJE", "CAB DES", "SEP EJE", "SEP DES",
                "APROX", "FORMA", "TIPO CORTE", "RADIO", "ETIQUETA", "OBSERVACIÓN"
            ]

            for columna in columnas_requeridas:
                if columna not in df.columns:
                    return f"Falta la columna '{columna}' en el Excel.", 400

            # Borrar datos anteriores
            Suaje.query.delete()

            # Insertar filas nuevas
            for _, row in df.iterrows():
                suaje = Suaje(
                    suaje=str(row["# SUAJE"]),
                    mag_sol=str(row["MAG/SOL"]),
                    medida=str(row["MEDIDA"]),
                    eje=str(row["EJE"]),
                    des=str(row["DES"]),
                    dt=str(row["DT"]),
                    cab_eje=str(row["CAB EJE"]),
                    cab_des=str(row["CAB DES"]),
                    sep_eje=str(row["SEP EJE"]),
                    sep_des=str(row["SEP DES"]),
                    aprox=str(row["APROX"]),
                    forma=str(row["FORMA"]),
                    tipo_corte=str(row["TIPO CORTE"]),
                    radio=str(row["RADIO"]),
                    etiqueta=str(row["ETIQUETA"]),
                    observacion=str(row["OBSERVACIÓN"])
                )
                db.session.add(suaje)

            db.session.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return f"Error al procesar el archivo: {e}", 500

    return render_template('importar.html')


if __name__ == '__main__':
    app.run(debug=True)