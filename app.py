import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
from modelb_dataset import *

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'csv', 'txt'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 5mb
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            # return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')

def process_file(path, filename):
    input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_file = Path(app.config['DOWNLOAD_FOLDER'], filename)
    from shutil import copyfile
    copyfile(input_file, app.config['DOWNLOAD_FOLDER'] + filename)
    return process_csv(input_file)

@app.route('/uploads/<filename>')
def uploaded_file(filename):

    print(filename)
    return "0"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '127.0.0.1')
