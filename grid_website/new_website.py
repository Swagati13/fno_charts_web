from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from datetime import datetime, timedelta
import random
import threading
import time
import os
import sqlite3
import requests
import pickle
from dateutil import parser

app = Flask(__name__)

secret_key = os.urandom(24)
app.secret_key = secret_key

DATABASE = '/home/mestha/Desktop/flask_tutorial/grid_website/mydatabase.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

def add_user(username, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()

def get_user(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            user = get_user(username)
            if user and user[2] == password:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('select_index'))
            else:
                return render_template('new_website_login.html', error='Invalid username or password')
        else:
            return redirect(url_for('signup'))  
    else:
        if 'logged_in' in session:
            return redirect(url_for('select_index'))  
        return render_template('new_website_login.html')

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('new_website_login.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/select_index', methods=['GET', 'POST'])
def select_index():
    if 'logged_in' in session:
        if request.method == 'POST':
            if 'action' in request.form:
                if request.form['action'] == 'Start':
                    index = request.form.get('index')
                    strike = request.form.get('strike')
                    option_type = request.form.get('option_type')
                    gridsize = request.form.get('gridsize')
                    maxgridsize=request.form.get('maxgrid')
                    lotsize = request.form.get('lotsize')

                    print("Index:",index)
                    print("strike:",strike)
                    print("option Type:",option_type)
                    print("Grid Size:",gridsize)
                    print("Maximum Grids:",maxgridsize)
                    print("Lots:",lotsize)
                    return render_template('select_index.html')
                
                elif request.form['action'] == 'Stop':
                    return render_template('select_index.html')
            else:
                return render_template('select_index.html')
        else:
            return render_template('select_index.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000,debug=True)