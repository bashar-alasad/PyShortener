from flask import Flask, request, redirect, render_template_string
import sqlite3
import random
import string

app = Flask(__name__)

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_random_short_link():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(6))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form.get('url')
        short_link = create_random_short_link()
        
        conn = get_db_connection()
        conn.execute('INSERT INTO urls (original_url, short_link) VALUES (?, ?)',
                     (original_url, short_link))
        conn.commit()
        conn.close()
        
        return f"Shortened URL is: <a href='/{short_link}'>/{short_link}</a>"
    return render_template_string('''
                                  <form method="post">
                                      <input type="text" name="url" placeholder="Enter your URL here" required>
                                      <input type="submit" value="Shorten">
                                  </form>
                                  ''')

@app.route('/<short_link>')
def redirect_to_original(short_link):
    conn = get_db_connection()
    url_data = conn.execute('SELECT original_url FROM urls WHERE short_link = ?',
                            (short_link,)).fetchone()
    conn.close()
    if url_data:
        return redirect(url_data['original_url'])
    return 'URL not found', 404

def setup_database():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, original_url TEXT, short_link TEXT)')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)