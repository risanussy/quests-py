from flask import Flask, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
app.secret_key = "KunciRahasiaUntukSesi"  # Kunci rahasia untuk sesi

@app.route('/')
def index():
    return "<h1>Flask API</h1>"

from flask_bcrypt import check_password_hash
from flask_bcrypt import Bcrypt
from flask import send_from_directory

bcrypt = Bcrypt(app)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = '154.41.240.154'
app.config['MYSQL_USER'] = 'u481547927_game_flask'
app.config['MYSQL_PASSWORD'] = '@Gam31234'
app.config['MYSQL_DB'] = 'u481547927_game_flask'

mysql = MySQL(app)
cors = CORS(app)

# @app.after_request
# def handle_options(response):
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"

#     return response

# Direktori untuk menyimpan file gambar
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Fungsi untuk mengizinkan ekstensi file gambar
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk melakukan login
@app.route('/api/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.check_password_hash(user[4], password):
            response = jsonify({'message': 'Login successful', 'username': username})
            response.headers['Cache-Control'] = 'no-cache'
            response.set_cookie('username', username)  # Simpan username dalam cookie
            return response, 200
        else:
            response = jsonify({'error': 'Invalid username or password'})
            response.headers['Cache-Control'] = 'no-cache'
            return response, 401

# Fungsi untuk melakukan registrasi
@app.route('/api/register', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, username, email, password, saldo, point) VALUES (%s, %s, %s, %s, %s, %s)", (name, username, email, hashed_password, 0, 0))
        mysql.connection.commit()
        cursor.close()
        response = jsonify({'message': 'Registration successful'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers['Cache-Control'] = 'no-cache'
        return response, 201

# Fungsi untuk logout
@app.route('/api/logout', methods=['GET'])
@cross_origin(supports_credentials=True)
def logout():
    session.pop('username', None)  # Hapus username dari sesi
    response = jsonify({'message': 'Logout successful'})
    response.headers['Cache-Control'] = 'no-cache'
    response.delete_cookie('username')  # Hapus cookie username
    return response, 200

# Fungsi untuk mendapatkan data pengguna berdasarkan username
@app.route('/api/user/<username>', methods=['GET'])
def get_user_by_username(username):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    print(user)
    if user:
        user_data = {
            'id': user[0],
            'name': user[1],
            'username': user[2],
            'email': user[3],
            'saldo': user[6],
            'point': user[5]
        }
        return jsonify({'user': user_data}), 200
    else:
        return jsonify({'error': 'User not found'}), 404


# Endpoint untuk menambahkan quest
@app.route('/api/quests', methods=['POST'])
def add_quest():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')

    # Masukkan data ke database
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO quest (name, user_id, level, timeout, created_by, answer) VALUES (%s, %s, %s, %s, %s, %s)",
                   (request.form['name'], request.form['user_id'], request.form['level'], request.form['timeout'], request.form['created_by'], request.form['answer']))
    # cursor.execute("INSERT INTO quest (name, user_id, level, timeout, created_by, answer) VALUES (%s, %s, %s, %s, %s, %s)",
    #                (request.form['name'], session['user_id'], request.form['level'], request.form['timeout'], request.form['created_by'], request.form['answer']))
    quest_id = cursor.lastrowid

    # Simpan gambar
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute("INSERT INTO quest_images (quest_id, filename) VALUES (%s, %s)", (quest_id, filename))

    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Quest added successfully'}), 201

# Fungsi untuk memperbarui nilai point pengguna berdasarkan username
@app.route('/api/user/update_point/<username>', methods=['POST'])
def update_user_point(username):
    # Ambil nilai point yang baru dari body permintaan
    new_point = request.json.get('point')

    # Pastikan nilai point yang diterima adalah bilangan bulat
    if not isinstance(new_point, int):
        return jsonify({'error': 'Point must be an integer'}), 400

    # Lakukan pembaruan nilai point pada database
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET point = %s WHERE username = %s", (new_point, username))
    mysql.connection.commit()
    cursor.close()

    # Periksa apakah pembaruan berhasil
    if cursor.rowcount > 0:
        return jsonify({'message': 'User point updated successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# Endpoint untuk mendapatkan semua quest beserta gambar-gambar
@app.route('/api/quests', methods=['GET'])
def get_quests():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM quest")
    quests = cursor.fetchall()
    cursor.close()

    result = []
    for quest in quests:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT filename FROM quest_images WHERE quest_id = %s", (quest[0],))
        images = cursor.fetchall()
        cursor.close()

        image_list = [image[0] for image in images]
        print(quest)
        result.append({
            'id': quest[0],
            'name': quest[1],
            'level': quest[3],
            'timeout': quest[4],
            'created_by': quest[5],
            'answer': quest[6],
            'created_at': quest[7],
            'updated_at': quest[8],
            'images': image_list
        })

    return jsonify(result), 200

@app.route('/api/played', methods=['POST'])
def add_played():
    # Pastikan permintaan memiliki payload JSON yang sesuai
    if not request.json or 'quest_id' not in request.json or 'user_id' not in request.json:
        return jsonify({'error': 'Invalid request format'}), 400
    
    # Ambil data dari payload
    quest_id = request.json['quest_id']
    user_id = request.json['user_id']
    answered = request.json.get('answered', None)  # Opsional, bisa kosong
    
    # Masukkan data ke dalam tabel played
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO played (quest_id, user_id, answered) VALUES (%s, %s, %s)",
                   (quest_id, user_id, answered))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Data added to played table successfully'}), 201

@app.route('/api/played/<int:played_id>', methods=['GET'])
def get_played_by_id(played_id):
    # Ambil data dari tabel played berdasarkan ID
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM played WHERE id = %s", (played_id,))
    played_data = cursor.fetchone()
    cursor.close()

    # Jika data tidak ditemukan, kembalikan respons 404
    if not played_data:
        return jsonify({'error': 'Data not found'}), 404

    # Jika data ditemukan, kembalikan respons dengan data yang ditemukan
    return jsonify({'played_data': played_data}), 200
# API untuk mendapatkan daftar semua pengguna dan quest yang mereka mainkan
@app.route('/api/users', methods=['GET'])
def get_users_with_quest():
    cursor = mysql.connection.cursor()
    try:
        # Query untuk mendapatkan daftar semua pengguna beserta quest yang mereka mainkan,
        # diurutkan berdasarkan poin pengguna secara terbalik (terbesar ke terkecil)
        query = """
            SELECT users.id, users.name, users.username, users.email, users.point, users.saldo, 
                   quest.id AS quest_id, quest.name AS quest_name, quest.level, quest.timeout, quest.created_by, quest.answer
            FROM users
            LEFT JOIN played ON users.id = played.user_id
            LEFT JOIN quest ON played.quest_id = quest.id
            ORDER BY users.point DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Mengelompokkan data pengguna dan quest yang mereka mainkan
        users = []
        for row in results:
            user_id = row[0]
            user_index = next((index for index, user in enumerate(users) if user['id'] == user_id), None)
            if user_index is None:
                users.append({
                    'id': row[0],
                    'name': row[1],
                    'username': row[2],
                    'email': row[3],
                    'point': row[4],
                    'saldo': row[5],
                    'quests': []
                })
                user_index = len(users) - 1

            if row[6]:  # Jika ada quest yang dimainkan oleh pengguna
                users[user_index]['quests'].append({
                    'id': row[6],
                    'name': row[7],
                    'level': row[8],
                    'timeout': row[9],
                    'created_by': row[10],
                    'answer': row[11]
                })

        # Mengembalikan data dalam format JSON
        return jsonify(users)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port_nr = int(os.environ.get("PORT", 5001))
    app.run(port=port_nr, host='0.0.0.0')
