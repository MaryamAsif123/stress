from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)

# Azure SQL Database Connection Details
SERVER = 'stresswebapp-server.database.windows.net'
DATABASE = 'stresswebapp-database'
USERNAME = 'stresswebapp-server-admin'
PASSWORD = 'NewSecurePassword123!'
DRIVER = '{ODBC Driver 17 for SQL Server}'

# Function to create a connection
def get_db_connection():
    conn = pyodbc.connect(
        f'DRIVER={DRIVER};SERVER={SERVER};PORT=1433;DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
    )
    return conn

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM Users")
    users = cursor.fetchall()
    conn.close()
    
    user_list = [
        {"id": row[0], "name": row[1], "email": row[2], "created_at": row[3].strftime("%Y-%m-%d %H:%M:%S")}
        for row in users
    ]
    return jsonify(user_list)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM Users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_data = {"id": user[0], "name": user[1], "email": user[2], "created_at": user[3].strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    
    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    new_email = data.get("email")
    
    if not new_email:
        return jsonify({"error": "Email is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET email = ? WHERE id = ?", (new_email, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User updated successfully"})

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
