import time

from flask import Flask, request, jsonify, render_template
from SDES import SDES, brute_force, brute_force_all

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    key = data.get('key', [])
    plaintext = data.get('text', [])
    sdes = SDES(key)
    ciphertext = sdes.encrypt(plaintext)
    return jsonify({"result": ciphertext})


@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    key = data.get('key', [])
    ciphertext = data.get('text', [])
    sdes = SDES(key)
    decrypted_text = sdes.decrypt(ciphertext)
    return jsonify({"result": decrypted_text})


@app.route('/encrypt_ascii', methods=['POST'])
def encrypt_ascii():
    data = request.json
    key = data.get('key', [])
    plaintext_str = data.get('text', "")
    sdes = SDES(key)
    ciphertext_str = sdes.encrypt_string(plaintext_str)
    return jsonify({"result": ciphertext_str})


@app.route('/decrypt_ascii', methods=['POST'])
def decrypt_ascii():
    data = request.json
    key = data.get('key', [])
    ciphertext_str = data.get('text', "")
    sdes = SDES(key)
    decrypted_str = sdes.decrypt_string(ciphertext_str)
    return jsonify({"result": decrypted_str})


@app.route('/brute_force', methods=['POST'])
def brute_force_route():
    data = request.json
    pairs = [
        {
            'plaintext': [int(bit) for bit in pair['plaintext']],
            'ciphertext': [int(bit) for bit in pair['ciphertext']],
        }
        for pair in data.get('pairs', [])
    ]
    pairs = [(pair['plaintext'], pair['ciphertext']) for pair in pairs]
    key, time_taken = brute_force(pairs)

    if key is not None:
        return jsonify({"key": key, "time_taken": time_taken})
    else:
        return jsonify({"error": "No key found"}), 404


@app.route('/brute_force_all', methods=['POST'])
def brute_force_all_route():
    data = request.json
    pairs = [
        {
            'plaintext': [int(bit) for bit in pair['plaintext']],
            'ciphertext': [int(bit) for bit in pair['ciphertext']],
        }
        for pair in data.get('pairs', [])
    ]
    pairs = [(pair['plaintext'], pair['ciphertext']) for pair in pairs]

    keys, time_taken = brute_force_all(pairs)

    if len(keys) > 0:
        return jsonify({"keys": keys, "time_taken": time_taken})
    else:
        return jsonify({"error": "No key found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
