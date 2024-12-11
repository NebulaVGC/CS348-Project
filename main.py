from flask import Flask, flash, render_template, jsonify, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route('/edit/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            conn = db_connect()
            cursor = conn.cursor()
            name = request.form.get('name')
            cmd = "CALL CheckName(%s, @total);"
            cursor.execute(cmd, (name,))
            cursor.execute("SELECT @total;")
            newName = cursor.fetchone()[0]
            
            if newName > 0:
                flash('This name is already taken. Please choose another name.')
                return redirect(url_for('add'))
            
            dex = request.form.get('dex-number')
            cmd = "CALL CheckDex(%s, @total);"
            cursor.execute(cmd, (dex,))
            cursor.execute("SELECT @total;")
            newDex = cursor.fetchone()[0]
            if newDex > 0:
                flash('This dex number is already taken. Please choose another dex number.')
                return redirect(url_for('add'))
            
            cmd = "CALL AddPokemon(%s, %s, %s, %s, %s,%s,%s,%s,%s,%s);"
            vals = [name, dex, request.form.get('type1'), request.form.get('type2'), request.form.get('hp'), request.form.get('attack'), request.form.get('defense'), request.form.get('special-attack'), request.form.get('special-defense'), request.form.get('speed')]
            cursor.execute(cmd, vals)
            conn.commit()
            flash('Pokémon added successfully!')
            cursor.close()
            conn.close()
            return redirect(url_for('add'))
            
        except Exception as e:
            print("Error:", e)
            flash("An error occurred. Please try again.")
            return redirect(url_for('add'))
    return render_template('add.html')

@app.route('/edit/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        try:
            conn = db_connect()
            cursor = conn.cursor()
            name = request.form.get('species')
            cmd = "CALL CheckNameUpdate(%s, %s, @total);"
            cursor.execute(cmd, (name, request.form.get("original_species")))
            cursor.execute("SELECT @total;")
            newName = cursor.fetchone()[0]
            
            if newName > 0:
                flash('This name is already taken. Please choose another name.')
                return redirect(url_for('update'))
            
            dex = request.form.get('dexID')
            cmd = "CALL CheckDexUpdate(%s, %s, @total);"
            cursor.execute(cmd, (dex, request.form.get("original_dexID")))
            cursor.execute("SELECT @total;")
            newDex = cursor.fetchone()[0]
            if newDex > 0:
                flash('This dex number is already taken. Please choose another dex number.')
                return redirect(url_for('update'))
            
            cmd = "CALL UpdatePokemon(%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s);"
            vals = [request.form.get("original_species"), name, dex, request.form.get('type1'), request.form.get('type2'), request.form.get('hp'), request.form.get('attack'), request.form.get('defense'), request.form.get('special-attack'), request.form.get('special-defense'), request.form.get('speed')]
            cursor.execute(cmd, vals)
            conn.commit()
            flash('Pokémon updated successfully!')
            cursor.close()
            conn.close()
            return redirect(url_for('update'))
            
        except Exception as e:
            print("Error:", e)
            flash("An error occurred. Please try again.")
            return redirect(url_for('update'))
    return render_template('update.html')

@app.route('/edit/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        try:
            conn = db_connect()
            cursor = conn.cursor()
            name = request.form.get('species')
            cmd = "CALL DeletePokemon(%s);"
            cursor.execute(cmd, [name])
            conn.commit()
            flash('Pokémon deleted successfully!')
            cursor.close()
            conn.close()
            return redirect(url_for('delete'))
            
        except Exception as e:
            print("Error:", e)
            flash("An error occurred. Please try again.")
            return redirect(url_for('delete'))
    return render_template('delete.html')

def db_connect():
    return mysql.connector.connect(
        host="DESKTOP-4G1VOHE.local",
        user="root2",
        passwd="1234",
        database="test"
    )

@app.route('/api/items', methods=['GET'])
def get_items():
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT species FROM Pokemon;")
        rows = cursor.fetchall()
        items = [{'name': row[0]} for row in rows]
        cursor.close()
        conn.close()
        return jsonify(items)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Could not fetch items"}), 500

@app.route('/api/item-details', methods=['GET'])
def get_item_details():
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cmd = "SELECT * FROM Pokemon WHERE species=%s;"
        species = [request.args.get('name')]
        cursor.execute(cmd, species)
        rows = cursor.fetchall()
        rows = rows[0]
        item = {
            'dexID': rows[0],
            'species': rows[1],
            'type1': rows[2],
            'type2': rows[3],
            'hp': rows[4],
            'attack': rows[5],
            'defense': rows[6],
            'spatk': rows[7],
            'spdef': rows[8],
            'speed': rows[9]
        }
        cursor.close()
        conn.close()
        return jsonify(item)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Could not fetch items"}), 500

if __name__ == "__main__":
    app.run(debug=True)
