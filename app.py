from flask import Flask, send_file, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'followers_file' not in request.files or 'following_file' not in request.files:
        flash("Files not found in request", 'error')
        return redirect(url_for('index'))

    followers_file = request.files['followers_file']
    following_file = request.files['following_file']

    if followers_file.filename == '' or following_file.filename == '':
        flash("One or both files are empty", 'error')
        return redirect(url_for('index'))

    if followers_file.filename.endswith('.html') and following_file.filename.endswith('.html'):
        if followers_file.filename != following_file.filename:  # Ensure files are not the same
            followers_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(followers_file.filename))
            following_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(following_file.filename))

            followers_file.save(followers_path)
            following_file.save(following_path)

            followers_list = parse_html(followers_path)
            following_list = parse_html(following_path)

            print("Followers List:", followers_list)
            print("Following List:", following_list)

            not_following_back = [{'username': user, 'instagram_id': user} for user in following_list if user not in followers_list]
            not_followed_back = [{'username': user, 'instagram_id': user} for user in followers_list if user not in following_list]

            print("Not Following Back:", not_following_back)
            print("Not Followed Back:", not_followed_back)

            return send_file('result.html', not_following_back=not_following_back, not_followed_back=not_followed_back)
        else:
            flash("Both files are the same", 'error')
            return redirect(url_for('index'))
    else:
        flash("Only HTML files are allowed", 'error')
        return redirect(url_for('index'))

def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        # Find all <a> tags
        username_tags = soup.find_all('a', href=True, target="_blank")
        
        # Extract usernames from the tags
        usernames = [tag.get_text(strip=True) for tag in username_tags]

        print("Extracted Usernames:", usernames)
        return usernames

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1001, debug=True)
