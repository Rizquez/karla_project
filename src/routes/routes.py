# -------------------------------------------------------------------------------------------------------------------------------------------------
# LIBRERIAS / APIs NECESARIAS
# -------------------------------------------------------------------------------------------------------------------------------------------------
import json
import pandas as pd
from io import BytesIO
from ..models import obtain_trees
from ..utils import create_xlsx_file, format_dataframe
from flask import Flask, render_template, redirect, request, send_file, jsonify
# -------------------------------------------------------------------------------------------------------------------------------------------------

# Instanciamos la app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Ruta raiz para el calculo
@app.route('/', methods=['GET', 'POST'])
def home():
    # Verificamos si se enviaron datos
    if request.method == 'POST':

        # Extraemos los datos de la peticion aplicando un casting segun el tipo de dato recibido
        co2_capture = float(request.form.get('co2-capture'))
        tree_number = int(request.form.get('tree-number'))

        # Verificamos la posibilidad de que el valor de la variable co2_capture sea un entero
        if co2_capture.is_integer():
            co2_capture = int(co2_capture)

        # Llamamos al metodo para realizar el filtrado sobre los datos introducidos por el usuario
        dct_tress = obtain_trees(tree_number, co2_capture)
        
        # Verificamos si dct_tress se encuentra vacio, esto indica que no hay arboles para la cantidad de 
        # CO2 señalada y crearemos un mensaje para el usuario, en caso contrario instanciamos la variable a None
        message = "Se recomienda agregar más unidades arbóreas para suplir las necesidades de captura indicadas 🌱" if not dct_tress else None

        # Renderizamos el template index con los datos a insertar
        return render_template('index.html', dct_tress=dct_tress, tree_number=tree_number, co2_capture=co2_capture, message=message)
    
    # Si no es POST, simplemente cargamos la pagina sin datos de resultado
    return render_template('index.html', dct_tress=None, tree_number=None, co2_capture=None, message=None)


# Ruta para descargar los documentos
@app.route('/download-table', methods=['POST'])
def download_table():
    # Constantes de calculo
    NAME_FILE = 'Guia de plantaciones monoespecificas.xlsx'
    NAME_SHEET = 'Especies Arbolada'
    NAME_TABLE = 'Tabla_Especies_Cumplen'
    FLOAT_FORMAT = '%.4f'

    # Primero que nada vamos a extraer el diccionario con los datos de los arboles filtrados
    request_data = request.form.get('json-data')
    lst_data = json.loads(request_data)
    
    # Creamos un DataFrame de pandas con los datos de la tabla
    df = pd.DataFrame(lst_data)

    # Formateamos el dataframe antes de almacenarlo
    df = format_dataframe(df)

    # Instanciamos y escribimos los datos en la ruta de salida que nos pasan como parametro
    # Usando un buffer en memoria para guardar el archivo Excel
    # Almacenando el dataframe con los diferentes parametros que nos interesan
    excel_file = BytesIO()
    create_xlsx_file(excel_file, NAME_TABLE, NAME_SHEET, df, 'w', FLOAT_FORMAT)

    # Movemos el puntero al inicio del buffer
    excel_file.seek(0)

    return send_file(
        excel_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=NAME_FILE
        )


@app.route('/download-group', methods=['POST'])
def download_group():
    # Constantes de calculo
    NAME_FILE = 'Grupo de plantaciones monoespecificas.xlsx'
    NAME_SHEET = 'Grupo Especies Arbolada'
    NAME_TABLE = 'Tabla_Grupo_Especies'
    FLOAT_FORMAT = '%.4f'

    # Extraemos la lista de datos
    lst_data = request.get_json()

    # Instanciamos un dataframe con los datos que se llevaran al excel
    df = pd.DataFrame(lst_data)

    # Formateamos el dataframe antes de almacenarlo
    df = format_dataframe(df)

    # Instanciamos y escribimos los datos en la ruta de salida que nos pasan como parametro
    # Usando un buffer en memoria para guardar el archivo Excel
    # Almacenando el dataframe con los diferentes parametros que nos interesan
    excel_file = BytesIO()
    create_xlsx_file(excel_file, NAME_TABLE, NAME_SHEET, df, 'w', FLOAT_FORMAT)

    # Movemos el puntero al inicio del buffer
    excel_file.seek(0)

    return send_file(
        excel_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=NAME_FILE
        )


# Manejador de errores mas comunes
@app.errorhandler(404)
@app.errorhandler(500)
def error_handler(error):
    return redirect('/error')


# Ruta para la salida de errores
@app.route('/error')
def error():
    return render_template("page_error.html")

# -------------------------------------------------------------------------------------------------------------------------------------------------
# FIN DEL FICHERO
# -------------------------------------------------------------------------------------------------------------------------------------------------