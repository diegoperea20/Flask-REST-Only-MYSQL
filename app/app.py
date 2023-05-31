from flask import Flask, jsonify, request, abort
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mypassword'
app.config['MYSQL_DB'] = 'myflaskapp'

mysql = MySQL()

# Inicializar la extensión Flask-MySQLdb
mysql.init_app(app)

# Crear la tabla "books" si no existe
def create_table():
    with app.app_context():
        with mysql.connection.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS books (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                description VARCHAR(255),
                author VARCHAR(255)
            )""")
        mysql.connection.commit()

create_table()

# Obtener todos los libros
@app.route('/books', methods=['GET'])
def get_books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from books")
    books = cur.fetchall()
    return jsonify({'books': books})

# Obtener un libro por su id
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    if book is None:
        abort(404)
    return jsonify({'book': book})

# Agregar un nuevo libro
@app.route('/books', methods=['POST'])
def create_book():
    if not request.json or not 'title' in request.json:
        abort(400)
    title = request.json['title']
    description = request.json.get('description', '')
    author = request.json.get('author', '')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO books (title, description, author) VALUES (%s, %s, %s)",
                (title, description, author))
    mysql.connection.commit()
    return jsonify({'book': {'title': title, 'description': description, 'author': author}}), 201

# Actualizar un libro
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    if book is None:
        abort(404)
    title = request.json.get('title', book[1])
    description = request.json.get('description', book[2])
    author = request.json.get('author', book[3])
    cur.execute("UPDATE books SET title = %s, description = %s, author = %s WHERE id = %s",
                (title, description, author, book_id))
    mysql.connection.commit()
    return jsonify({'book': {'title': title, 'description': description, 'author': author}})

# Eliminar un libro
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    if book is None:
        abort(404)
    cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
    mysql.connection.commit()
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run()

#Comands for use docker container mysql
#docker run --name mymysql -e MYSQL_ROOT_PASSWORD=mypassword -p 3306:3306 -d mysql:latest
#docker exec -it mymysql bash
#mysql -u root -p
#create database myflaskapp;