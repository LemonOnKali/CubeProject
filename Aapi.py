from flask import Flask, jsonify
import board
import busio
import adafruit_bme280

app = Flask(__name__)

# Initialise le bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialise le capteur BME280
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    try:
        # Lit les données du capteur
        temperature = bme280.temperature
        humidity = bme280.humidity
        pressure = bme280.pressure

        # Formate les données
        data = {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure
        }

        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': f'Erreur de lecture du capteur : {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
