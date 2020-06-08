import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file
from matplotlib import image
from werkzeug.utils import secure_filename
from pathlib import Path
from modelb_dataset import *

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
PROCESSED_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '\\processed\\'
ALLOWED_EXTENSIONS = {'csv', 'txt'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
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
            outputs= process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            user_table = outputs[0]
            user_image = outputs[1]
            return render_template('results.html', user_image=user_image, tables=[user_table], file_name = filename)
    return render_template('index.html')

def process_file(path, filename):
    input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_file = Path(app.config['DOWNLOAD_FOLDER'], filename)
    from shutil import copyfile
    copyfile(input_file, app.config['DOWNLOAD_FOLDER'] + filename)
    return process_csv(input_file, filename)

def get_image(path, filename):
    import io
    output = io.BytesIO()
    image.convert('RGBA').save(output, format='PNG')
    output.seek(0, 0)

    return send_file(output, mimetype='image/png', as_attachment=False)

@app.route('/testimage')
def get_testimage():

    testimage = request.values.get("file_name")

    if str(testimage).endswith(".csv"):
        filename = str(testimage).replace(".csv",".png")
    elif str(testimage).endswith(".txt"):
        filename = str(testimage).replace(".txt", ".png")

    if testimage == '':
        testimage = os.path.join(app.config['PROCESSED_FOLDER'], 'sample.png')
    else:
        testimage = os.path.join(app.config['PROCESSED_FOLDER'], filename)

    return send_file(testimage, mimetype='image/png')
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '127.0.0.1')
