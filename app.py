from flask import Flask, request, jsonify
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from flask_cors import CORS

# Charger les configurations depuis .env
load_dotenv()

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', '')
}

# Initialisation de la base de données
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.close()
    print("Connected to the database...")
except Error:
    print("Error connecting to the database")

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        number1 = data['number1']
        number2 = data['number2']
        operator = data['operator']

        if operator == '+':
            result = number1 + number2
        elif operator == '-':
            result = number1 - number2
        elif operator == '*':
            result = number1 * number2
        elif operator == '/':
            if number2 == 0:
                return jsonify({'error': 'Division by zero is not allowed'}), 400
            result = number1 / number2
        else:
            return jsonify({'error': 'Invalid operator'}), 400

        # Enregistrer le calcul dans la base de données
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO calculations (number1, number2, operator, result) VALUES (%s, %s, %s, %s)", (number1, number2, operator, result))
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'result': result})

    except KeyError:
        return jsonify({'error': 'Invalid input data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, number1, number2, operator, result FROM calculations")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        history = [
            {
                'id': row[0],
                'number1': row[1],
                'number2': row[2],
                'operator': row[3],
                'result': row[4]
            } for row in rows
        ]

        return jsonify(history)

    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hello', methods=['GET'])
def hello_world():
    return "Hello, World!"

@app.route('/whoami', methods=['GET'])
def whoami():
    return os.getenv('HOSTNAME', 'No hostname set')

if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug)

