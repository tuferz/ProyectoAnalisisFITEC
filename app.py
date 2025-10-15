from flask import Flask, render_template, request
import pandas as pd
import pyodbc
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
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

        linea_prediccion = modelo.predict(X)

        anios = df['Anio'].tolist()
        reales = df['TotalIngresos'].tolist()
        predichos = linea_prediccion.tolist()

        return render_template(
            'regresion_simple.html',
            beta0=f"{beta_0:.2f}",
            beta1=f"{beta_1:.2f}",
            anios_json=anios,
            reales_json=reales,
            predichos_json=predichos,
            titulo=titulo,
            descripcion=descripcion
        )

    except Exception as e:
        return f"<h1>Ocurrió un error en la aplicación</h1><p><strong>Detalle:</strong> {e}</p>"


# @app.route('/regresion_multiple')
if __name__ == '__main__':
    app.run(debug=True)
