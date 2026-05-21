import pytest
import io
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:

    def test_health_returns_200(self, client):
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get('/health')
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestPagesLoad:

    def test_index_page(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_upload_page(self, client):
        response = client.get('/upload')
        assert response.status_code == 200

    def test_result_page(self, client):
        response = client.get('/result')
        assert response.status_code == 200

    def test_404(self, client):
        response = client.get('/nonexistent-route')
        assert response.status_code == 404


class TestPredictEndpoint:

    def _make_txt_resume(self, content: str) -> io.BytesIO:
        return io.BytesIO(content.encode('utf-8'))

    def test_predict_no_file_returns_400(self, client):
        response = client.post('/predict')
        assert response.status_code == 400

    def test_predict_empty_filename_returns_400(self, client):
        data = {'resume': (io.BytesIO(b""), '')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_predict_txt_resume_returns_200(self, client):
        resume_text = b"""Jane Doe
jane@example.com
+91 9876543210
linkedin.com/in/janedoe

Skills: Python, Machine Learning, TensorFlow, Docker, AWS
Education: B.Tech Computer Science
3 years of experience in AI/ML
"""
        data = {
            'resume': (io.BytesIO(resume_text), 'resume.txt')
        }
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'data' in result
        assert 'matches' in result['data']
        assert 'skills' in result['data']

    def test_predict_unsupported_format_returns_415(self, client):
        data = {
            'resume': (io.BytesIO(b"some content"), 'resume.exe')
        }
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 415


class TestSkillsEndpoint:

    def test_skills_taxonomy_returns_200(self, client):
        response = client.get('/api/skills')
        assert response.status_code == 200

    def test_skills_taxonomy_is_dict(self, client):
        response = client.get('/api/skills')
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'programming_languages' in data


class TestTrainEndpoint:

    def test_train_without_key_returns_401(self, client):
        response = client.post('/train')
        assert response.status_code == 401

    def test_train_with_wrong_key_returns_401(self, client):
        response = client.post('/train', headers={'X-API-Key': 'wrong-key'})
        assert response.status_code == 401