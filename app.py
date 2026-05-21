import os
import sys
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

from src.logger import logger
from src.exception import ResumeScreenerException
from src.pipeline.prediction_pipeline import PredictionPipeline

# ─── App Setup ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit
app.config['UPLOAD_FOLDER'] = 'artifacts/raw'

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

# ─── Global Pipeline (loaded once) ───────────────────────────────────────────
print("DEBUG: Starting PredictionPipeline initialization...")
pipeline = PredictionPipeline(top_k=5)
print("DEBUG: PredictionPipeline initialized successfully!")


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def index():
    """Home page with upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['GET'])
def upload_page():
    """Dedicated upload page."""
    return render_template('upload.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    POST /predict
    Accepts multipart/form-data with 'resume' file.
    Returns JSON with matches and skill analysis.
    """
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded. Key should be "resume"'}), 400

        file = request.files['resume']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 415

        filename = secure_filename(file.filename)
        logger.info(f"Processing upload: {filename}")

        file_bytes = file.read()
        result = pipeline.predict_from_bytes(file_bytes, filename)

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except ResumeScreenerException as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500


@app.route('/result', methods=['GET'])
def result_page():
    """Result display page (for form-based flow)."""
    return render_template('result.html')


@app.route('/train', methods=['POST'])
def train():
    """
    POST /train
    Trigger training pipeline (admin endpoint).
    Protect with API key in production.
    """
    try:
        api_key = request.headers.get('X-API-Key', '')
        expected_key = os.environ.get('TRAIN_API_KEY', 'train-secret')
        if api_key != expected_key:
            return jsonify({'error': 'Unauthorized'}), 401

        from src.pipeline.training_pipeline import TrainingPipeline
        tp = TrainingPipeline()
        report = tp.run()
        pipeline.reload_jobs()
        return jsonify({'success': True, 'report': report}), 200

    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Docker/AWS."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Resume Screener',
        'version': '1.0.0',
    }), 200


@app.route('/api/skills', methods=['GET'])
def get_skill_taxonomy():
    """Return the full skill taxonomy for frontend."""
    from src.skill_extractor import SKILL_TAXONOMY
    return jsonify(SKILL_TAXONOMY), 200


# ─── Error Handlers ──────────────────────────────────────────────────────────

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({'error': 'File too large. Max size is 10MB'}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    logger.info(f"Starting Flask app on port {port} — debug={debug}")
    print(f"\n✓ Flask app starting on http://localhost:{port}/\n")
    sys.stdout.flush()
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)