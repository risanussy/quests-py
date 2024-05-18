from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.secret_key = "KunciRahasiaUntukSesi"  # Kunci rahasia untuk sesi

# Konfigurasi SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_flask.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
cors = CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Model untuk Database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    saldo = db.Column(db.Integer, default=0)
    point = db.Column(db.Integer, default=0)

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    level = db.Column(db.Integer)
    timeout = db.Column(db.Integer)
    created_by = db.Column(db.String(100))
    answer = db.Column(db.String(200))

class QuestImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quest_id = db.Column(db.Integer, db.ForeignKey('quest.id'))
    filename = db.Column(db.String(100))

class Played(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quest_id = db.Column(db.Integer, db.ForeignKey('quest.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answered = db.Column(db.String(200), nullable=True)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    harga = db.Column(db.Integer)
    nama = db.Column(db.String(100))
    deskripsi = db.Column(db.String(200))
    kategori = db.Column(db.String(100))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(100))

# Inisialisasi database
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return "<h1>Flask API</h1>"

# Fungsi untuk melakukan login
@app.route('/api/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
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

        new_user = User(name=name, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
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
    user = User.query.filter_by(username=username).first()
    if user:
        user_data = {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'email': user.email,
            'saldo': user.saldo,
            'point': user.point
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

    new_quest = Quest(
        name=request.form['name'],
        user_id=request.form['user_id'],
        level=request.form['level'],
        timeout=request.form['timeout'],
        created_by=request.form['created_by'],
        answer=request.form['answer']
    )
    db.session.add(new_quest)
    db.session.commit()
    quest_id = new_quest.id

    # Simpan gambar
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_image = QuestImage(quest_id=quest_id, filename=filename)
            db.session.add(new_image)

    db.session.commit()
    return jsonify({'message': 'Quest added successfully'}), 201

# Fungsi untuk memperbarui nilai point pengguna berdasarkan username
@app.route('/api/user/update_point/<username>', methods=['POST'])
def update_user_point(username):
    new_point = request.json.get('point')

    if not isinstance(new_point, int):
        return jsonify({'error': 'Point must be an integer'}), 400

    user = User.query.filter_by(username=username).first()
    if user:
        user.point = new_point
        db.session.commit()
        return jsonify({'message': 'User point updated successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# Endpoint untuk mendapatkan semua quest beserta gambar-gambar
@app.route('/api/quests', methods=['GET'])
def get_quests():
    quests = Quest.query.all()
    result = []
    for quest in quests:
        images = QuestImage.query.filter_by(quest_id=quest.id).all()
        image_list = [image.filename for image in images]
        result.append({
            'id': quest.id,
            'name': quest.name,
            'level': quest.level,
            'timeout': quest.timeout,
            'created_by': quest.created_by,
            'answer': quest.answer,
            'images': image_list
        })
    return jsonify(result), 200

# Endpoint untuk menambahkan data played
@app.route('/api/played', methods=['POST'])
def add_played():
    if not request.json or 'quest_id' not in request.json or 'user_id' not in request.json:
        return jsonify({'error': 'Invalid request format'}), 400

    new_played = Played(
        quest_id=request.json['quest_id'],
        user_id=request.json['user_id'],
        answered=request.json.get('answered', None)
    )
    db.session.add(new_played)
    db.session.commit()
    return jsonify({'message': 'Data added to played table successfully'}), 201

# Endpoint untuk mendapatkan data played berdasarkan ID
@app.route('/api/played/<int:played_id>', methods=['GET'])
def get_played_by_id(played_id):
    played_data = Played.query.get(played_id)
    if played_data:
        return jsonify({'played_data': played_data}), 200
    else:
        return jsonify({'error': 'Data not found'}), 404

# Endpoint untuk mendapatkan daftar semua pengguna dan quest yang mereka mainkan
@app.route('/api/users', methods=['GET'])
def get_users_with_quest():
    users = User.query.order_by(User.point.desc()).all()
    result = []
    for user in users:
        user_quests = Played.query.filter_by(user_id=user.id).all()
        quests = []
        for played in user_quests:
            quest = Quest.query.get(played.quest_id)
            if quest:
                quests.append({
                    'id': quest.id,
                    'name': quest.name,
                    'answered': played.answered
                })
        result.append({
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'email': user.email,
            'saldo': user.saldo,
            'point': user.point,
            'quests': quests
        })
    return jsonify(result), 200

# Endpoint untuk menambahkan store
@app.route('/api/store', methods=['POST'])
def add_store():
    if not request.json:
        return jsonify({'error': 'Invalid request format'}), 400

    new_store = Store(
        user_id=request.json['user_id'],
        harga=request.json['harga'],
        nama=request.json['nama'],
        deskripsi=request.json['deskripsi'],
        kategori=request.json['kategori']
    )
    db.session.add(new_store)
    db.session.commit()
    return jsonify({'message': 'Store added successfully'}), 201

# Endpoint untuk menambahkan transaksi
@app.route('/api/transaction', methods=['POST'])
def add_transaction():
    if not request.json:
        return jsonify({'error': 'Invalid request format'}), 400

    new_transaction = Transaction(
        store_id=request.json['store_id'],
        user_id=request.json['user_id'],
        status=request.json['status']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction added successfully'}), 201

# Endpoint untuk mendapatkan daftar store
@app.route('/api/store', methods=['GET'])
def get_store():
    stores = Store.query.all()
    result = []
    for store in stores:
        result.append({
            'id': store.id,
            'user_id': store.user_id,
            'harga': store.harga,
            'nama': store.nama,
            'deskripsi': store.deskripsi,
            'kategori': store.kategori
        })
    return jsonify(result), 200

# Endpoint untuk mendapatkan daftar transaksi
@app.route('/api/transaction', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    result = []
    for transaction in transactions:
        result.append({
            'id': transaction.id,
            'store_id': transaction.store_id,
            'user_id': transaction.user_id,
            'status': transaction.status
        })
    return jsonify(result), 200

# Endpoint untuk mengunduh gambar berdasarkan nama file
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Menjalankan aplikasi
if __name__ == '__main__':
    port_nr = int(os.environ.get("PORT", 5001))
    app.run(port=port_nr, host='0.0.0.0')
