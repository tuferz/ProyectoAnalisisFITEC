from flask import Flask, render_template
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
        cnxn = pyodbc.connect(connection_string)
        sql_query = """
            SELECT
                Anio,
                (ISNULL(IIS, 0) + ISNULL(ISC, 0) + ISNULL(IETE, 0) + ISNULL(IGTI, 0) + ISNULL(ITIC, 0) + ISNULL(LASC, 0)) AS TotalIngresos
            FROM
                Ingresos
            ORDER BY
                Anio;
        """
        df_ingresos = pd.read_sql(sql_query, cnxn)
        cnxn.close()

        X = df_ingresos['Anio'].values.reshape(-1, 1)
        Y = df_ingresos['TotalIngresos'].values

        modelo = LinearRegression()
        modelo.fit(X, Y)

        beta_1 = modelo.coef_[0]
        beta_0 = modelo.intercept_

        return render_template('index.html', ecuacion=f"Y = {beta_0:.2f} + {beta_1:.2f} * X", beta0=f"{beta_0:.2f}", beta1=f"{beta_1:.2f}")

    except Exception as e:
        return f"<h1>Ocurrió un error en la aplicación</h1><p><strong>Detalle:</strong> {e}</p>"


if __name__ == '__main__':
    app.run(debug=True)
