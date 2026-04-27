from functools import wraps
from flask import Blueprint, request, jsonify, send_file
from models import ApiToken, User
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from tools.pdf import *
from pycking_test import *
from io import BytesIO
import tempfile
import os
from models import db

api_bp = Blueprint('api', __name__, url_prefix='/api')


def require_api_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Требуется Bearer токен req',
                            'example': 'Authorization: Bearer ваш_токен'}), 401

        token_string = auth_header.split('Bearer ')[1]
        user = ApiToken.verify_token(token_string)

        if not user:
            return jsonify({'error': 'Bad token'}), 401

        return f(user, *args, **kwargs)

    return decorated


@api_bp.route('/token', methods=['POST'])
def get_token():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password is req'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Bad login data'}), 401

    token = ApiToken(
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(token)
    db.session.commit()

    return jsonify({
        'token': token.token,
        'expires_at': token.expires_at.isoformat(),
        'note': 'Используйте: Authorization: Bearer ваш_токен'
    }), 201


@api_bp.route('/revoke-token', methods=['POST'])
@require_api_token
def revoke_token(current_user):
    auth_header = request.headers.get('Authorization')
    token_string = auth_header.split('Bearer ')[1]

    token = ApiToken.query.filter_by(token=token_string).first()
    if token:
        token.is_active = False
        db.session.commit()
        return jsonify({'message': 'Token expired'}), 200

    return jsonify({'error': 'Bad token'}), 404


@api_bp.route('/process', methods=['POST'])
@require_api_token
def process_pdf_api(current_user):

    if 'file' not in request.files:
        return jsonify({'error': 'No file',
                        'required': 'multipart/form-data с полем "file"'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'umom?'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'PDF ONLY'}), 400

    try:
        width = int(request.form.get('width', 0))
        height = int(request.form.get('height', 0))
    except ValueError:
        return jsonify({'error': 'width и height должны быть int пж'}), 400

    algorithm = request.form.get('algorithm', '')
    allowed_algorithms = ['genetic', 'shelf', 'left-first-fit']

    if algorithm not in allowed_algorithms:
        return jsonify({
            'error': 'Недопустимый алгоритм',
            'allowed': allowed_algorithms
        }), 400

    # SAME
    file_data = file.read()

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_input:
        tmp_input.write(file_data)

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_output:
        output_path = tmp_output.name

    pypack(tmp_input.name, width, height, name=output_path)

    with open(output_path, 'rb') as f:
        processed_data = f.read()

    processed_pdf = BytesIO(processed_data)

    for path in [tmp_input.name, output_path]:
        if os.path.exists(path):
            os.unlink(path)

    return send_file(
        processed_pdf,
        as_attachment=True,
        download_name=f'processed_{file.filename}',
        mimetype='application/pdf'
    )


@api_bp.route('/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'ok',
        'version': '1.0',
        'endpoints': {
            'POST /api/token': 'Получить токен',
            'POST /api/process': 'Обработать pdf',
            'GET /api/status': 'Статус',
            'POST /api/revoke-token': 'Забрать токен'
        }
    })


@api_bp.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too big'}), 413


@api_bp.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Bad endpoint'}), 404