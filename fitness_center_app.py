from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error
from password import mypassword # probably will want to get rid of this one

app = Flask(__name__)
ma = Marshmallow(app)

class MembersSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.String(required=True)

    class Meta:
        fields = ('id', 'name', 'age')

class WorkoutSessionsSchema(ma.Schema):
    member_id = fields.String(required=True)
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ('session_id', 'member_id', 'session_date', 'session_time', 'activity')

member_schema = MembersSchema()
members_schema = MembersSchema(many=True)
workout_session_schema = WorkoutSessionsSchema()
workout_sessions_schema = WorkoutSessionsSchema(many=True)


def get_db_connection(): # fill the following four variables with your own mysql database info
    db_name = 'ManagingAFitnessCenter'
    user = 'root'
    password = mypassword # I have a file (not included that contains this info)
    host = '127.0.0.1'
    
    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
            )

        print("Connected to MySQL database successfully.")
        return conn
    
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def home():
    return  'Welcome to the Fitness Center!'

@app.route("/members", methods=["GET"])
def get_all_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members"

        cursor.execute(query)

        members = cursor.fetchall()

        return members_schema.jsonify(members)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:id>", methods=["GET"])
def get_member_by_id(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members WHERE id = %s"

        cursor.execute(query, (id,))
        member = cursor.fetchone()

        return member_schema.jsonify(member)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        new_member = (member_data['name'], member_data['age'])

        query = "INSERT INTO Members (name, age) VALUES (%s, %s)"

        cursor.execute(query, new_member)
        conn.commit()

        return jsonify({"message": "New member added successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_member = (member_data['name'], member_data['age'], id)

        query = "UPDATE Members SET name = %s, age = %s WHERE id = %s"

        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member updated successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
 
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        member_to_remove = (id,)

        cursor.execute("SELECT * FROM Members WHERE id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"Error": "member not found"}), 404
        
        query = "DELETE FROM Members WHERE id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()

        return jsonify({"message": "Member removed successfully"}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/sessions", methods=["GET"])
def get_all_sessions():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM WorkoutSessions"

        cursor.execute(query)

        sessions = cursor.fetchall()

        return workout_sessions_schema.jsonify(sessions)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/sessions/<int:id>", methods=["GET"])
def get_session_by_id(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM WorkoutSessions WHERE session_id = %s"

        cursor.execute(query, (id,))
        session = cursor.fetchone()

        return workout_session_schema.jsonify(session)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/sessions/member/<int:id>", methods=["GET"])
def get_session_by_member_id(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM WorkoutSessions WHERE member_id = %s"

        cursor.execute(query, (id,))
        sessions = cursor.fetchall()

        return workout_sessions_schema.jsonify(sessions)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/sessions", methods=["POST"])
def schedule_session():
    try:
        session_data = workout_session_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        new_session = (session_data['member_id'], session_data['session_date'], session_data['session_time'], session_data['activity'])

        query = "INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"

        cursor.execute(query, new_session)
        conn.commit()

        return jsonify({"message": "New session added successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/sessions/<int:id>", methods=["PUT"])
def update_session(id):
    try:
        session_data = workout_session_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_session = (session_data['member_id'], session_data['session_date'], session_data['session_time'], session_data['activity'], id)

        query = "UPDATE WorkoutSessions SET member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id = %s"

        cursor.execute(query, updated_session)
        conn.commit()

        return jsonify({"message": "Session updated successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/sessions/<int:id>", methods=["DELETE"])
def delete_session(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        session_to_remove = (id,)

        cursor.execute("SELECT * FROM WorkoutSessions WHERE session_id = %s", session_to_remove)
        session = cursor.fetchone()
        if not session:
            return jsonify({"Error": "member not found"}), 404
        
        query = "DELETE FROM WorkoutSessions WHERE session_id = %s"
        cursor.execute(query, session_to_remove)
        conn.commit()

        return jsonify({"message": "Session removed successfully"}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
