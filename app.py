from flask import Flask, render_template, request
import pandas as pd
import pyodbc
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

@app.template_filter('smartnum')
def smartnum(value):
    # Nulos -> vacío
    if value is None:
        return ''
    # NaN (floats)
    try:
        if isinstance(value, float) and pd.isna(value):
            return ''
    except Exception:
        pass
    # enteros (incluye numpy integer)
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    # floats (incluye numpy floating)
    if isinstance(value, (float, np.floating)):
        if float(value).is_integer():
            return str(int(round(value)))
        s = f"{value:.6f}".rstrip('0').rstrip('.')
        return s
    # pandas Timestamp u otros datetimes
    if isinstance(value, pd.Timestamp):
        return str(value)
    # resto (strings, bools, etc.)
    return str(value)

SERVER = 'SAM'
DATABASE = 'AnalisisFITEC'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/regresion_simple')
def dashboard_regresion_simple():
    tabla = request.args.get('tabla', 'Ingresos')
    try:
        cnxn = pyodbc.connect(connection_string)
        if tabla == 'Ingresos':
            sql_query = """
                SELECT Anio,(ISNULL(IIS, 0) + ISNULL(ISC, 0) + ISNULL(IETE, 0) + ISNULL(IGTI, 0) + ISNULL(ITIC, 0) + ISNULL(LASC, 0)) AS TotalIngresos
                FROM Ingresos
                ORDER BY Anio;
            """
            titulo = "Ingresos Anuales"
            descripcion = "Este modelo analiza la tendencia del número total de estudiantes que ingresan a la facultad cada año."
        elif tabla == 'Egresos':
            sql_query = """
                SELECT Anio,(ISNULL(IIS, 0) + ISNULL(ISC, 0) + ISNULL(IETE, 0) + ISNULL(IGTI, 0) + ISNULL(ITIC, 0) + ISNULL(LASC, 0)) AS TotalIngresos
                FROM Egresos
                ORDER BY Anio;
            """
            titulo = "Egresos Anuales"
            descripcion = "Este modelo analiza la tendencia del número total de estudiantes que egresan de la facultad cada año."
        else:
            return "<h1>Tabla no válida!</h1>"
        df = pd.read_sql(sql_query, cnxn)
        cnxn.close()

        df = df[df['TotalIngresos'] > 0]
        X = df['Anio'].values.reshape(-1, 1)
        Y = df['TotalIngresos'].values

        modelo = LinearRegression()
        modelo.fit(X, Y)

        beta_1 = modelo.coef_[0]
        beta_0 = modelo.intercept_

        r2 = modelo.score(X, Y)

        r = df['Anio'].corr(df['TotalIngresos'])

        linea_prediccion = modelo.predict(X)

        anios = df['Anio'].tolist()
        reales = df['TotalIngresos'].tolist()
        predichos = linea_prediccion.tolist()

        return render_template(
            'regresion_simple.html',
            beta0=f"{beta_0:.2f}",
            beta1=f"{beta_1:.2f}",
            r=f"{r:.4f}" if pd.notna(r) else "NA",
            r2=f"{r2:.4f}",
            anios_json=anios,
            reales_json=reales,
            predichos_json=predichos,
            titulo=titulo,
            descripcion=descripcion
        )

    except Exception as e:
        return f"<h1>Ocurrió un error en la aplicación</h1><p><strong>Detalle:</strong> {e}</p>"


# Nueva ruta: mostrar tabla dinámica (Ingresos / Egresos)
@app.route('/tabla')
def mostrar_tabla():
    tabla = request.args.get('tabla', 'Ingresos')
    try:
        cnxn = pyodbc.connect(connection_string)
        if tabla == 'Ingresos':
            sql = "SELECT * FROM Ingresos ORDER BY Anio;"
            titulo = 'Tabla - Ingresos'
        elif tabla == 'Egresos':
            sql = "SELECT * FROM Egresos ORDER BY Anio;"
            titulo = 'Tabla - Egresos'
        else:
            return "<h1>Tabla no válida!</h1>"

        df = pd.read_sql(sql, cnxn)
        cnxn.close()

        # Preparar columnas y filas para la plantilla (enviar datos crudos)
        cols = df.columns.tolist()
        rows = df.to_dict(orient='records')

        return render_template('tabla.html', titulo=titulo, cols=cols, rows=rows, tabla=tabla)

    except Exception as e:
        return f"<h1>Ocurrió un error al obtener la tabla</h1><p><strong>Detalle:</strong> {e}</p>"


# @app.route('/regresion_multiple')
if __name__ == '__main__':
    app.run(debug=True)
