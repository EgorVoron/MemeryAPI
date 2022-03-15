import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from API.python_utils import timeit
from API.python_utils import api_ok, api_error
from API.image_handling import ImageInfo, presave_img, text2pic, pic2pic

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def file_is_safe(file):
    return file and allowed_file(file.filename)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

logging.getLogger('flask_cors').level = logging.DEBUG
CORS(app, supports_credentials=True, origin='http://localhost:8080')


@timeit
@app.route('/api/upload', methods=['POST'])
def upload_img():
    file = request.files['image']
    if not file_is_safe(file):
        return api_error(400, 'WRONG_FORMAT')
    img = ImageInfo(file)
    result = presave_img(img)
    return jsonify(result)


@timeit
@app.route('/api/search/text', methods=['POST'])
def find_photo():
    user_text = request.json.get('query')
    pic_names = text2pic(user_text)
    return jsonify(api_ok({'count': len(pic_names), 'pic_paths': pic_names}))


@timeit
@app.route('/api/search/image', methods=['POST'])
def find_same():
    file = request.files['image']
    if not file_is_safe(file):
        return api_error(400, 'WRONG_FORMAT')
    pic_names = pic2pic(file)
    return jsonify(api_ok({'count': len(pic_names), 'pic_paths': pic_names}))
