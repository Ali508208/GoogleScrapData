from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from scraper import scrape_google_maps_with_api
from functools import wraps
from flask import flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SESSION_COOKIE_SECURE'] = True

# Hardcoded login details
USERNAME = "admin@gmail.com"
PASSWORD = "12345678"

# Global variable to control scraping
stop_scraping_flag = False

# Scraping thread to avoid blocking the main thread
scraping_thread = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == USERNAME and password == PASSWORD:
            session['user'] = email
            session.permanent = True  # Make session permanent
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"})
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None) 
    return render_template('login.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    api_key = "AIzaSyCJPY7sY1e9xrjnHhclgdiJxHTP3ohmaoo"
    data = request.json
    industry = data.get('industry')
    country = data.get('country')
    city = data.get('city')

    # Call scraping function
    results = scrape_google_maps_with_api(api_key,industry, city,country)

    return jsonify({"results": list(results)})

if __name__ == "__main__":
    app.run(debug=True)
