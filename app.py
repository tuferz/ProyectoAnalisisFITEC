from flask import Flask
import pandas as pd
import pyodbc
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
SERVER = 'SAM'
DATABASE = 'AnalisisFITEC'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"

@app.route('/')
def calcular_y_mostrar_regresion():
    try:
        conexion = pyodbc.connect(connection_string)
        sql_query = """
            SELECT
                Anio,
                (ISNULL(IIS, 0) + ISNULL(ISC, 0 ) + ISNULL(IETE,0) + ISNULL(IGTI, 0) + ISNULL(ITIC, 0) + ISNULL(LASC, 0)) AS IngresosTotales
            FROM
                Ingresos
            ORDER BY
                Anio;
        """
        df_ingresos = pd.read_sql_query(sql_query, conexion)
        conexion.close()
        X = df_ingresos['Anio'].values.reshape(-1,1)
        Y = df_ingresos['IngresosTotales'].values

        modelo = LinearRegression()
        modelo.fit(X, Y)

        beta_1=modelo.coef_[0]
        beta_0=modelo.intercept_

        html_respuesta = f"""
        <html>
            <head>
                <title>Análisis de Regresión FITEC</title>
                <style>
                    body  {{ font-family: Arial, sans-serif; margin: 2em; background-color: #f9f9f9; color: #333; }}
                    h1 {{ color: #005A9C; }}
                    .container {{ max-width: 800px; margin: auto; background-color: white; padding: 2em; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .ecuacion {{ background-color: #e7f3ff; border-left: 5px solid #005A9C; padding: 1.5em; margin: 1.5em 0; font-size: 1.4em; font-family: monospace; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Resultados del modelo de regresion simple</h1>
                    <h2>Prediccion del total de ingresos anuales</h2>
                    
                    <p>La ecuacion matematica que modela la tendencia de los ingresos es:</p>
                    <div class="ecuacion">
                        Y = {beta_0:.2f} + {beta_1:.2f} * X
                    </div>
                </div> 
            </body>
        </html>    
        """
        return html_respuesta
    except Exception as e:
        return f"<h1>Ocurrio un error en la aplicacion</h1><p><strong>Detalle:</strong> {e}</p>"

if __name__ == '__main__':
    app.run(debug=True)
