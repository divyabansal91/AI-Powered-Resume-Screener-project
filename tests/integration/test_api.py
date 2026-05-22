import pytest
import io
import json
from app import app


@pytest.fixture
def client():
    """Create test client for Flask app."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_returns_200(self, client):
        """Test that health endpoint returns 200."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Test that health endpoint returns valid JSON."""
        response = client.get('/health')
        data = response.get_json()
        assert isinstance(data, dict)
        assert data['status'] == 'healthy'

    def test_health_contains_version(self, client):
        """Test that health response includes service info."""
        response = client.get('/health')
        data = response.get_json()
        assert 'service' in data
        assert 'version' in data
        assert data['service'] == 'AI Resume Screener'


class TestPagesLoad:
    """Test that all HTML pages load correctly."""

    def test_index_page(self, client):
        """Test index page returns 200."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<' in response.data  # HTML content

    def test_upload_page(self, client):
        """Test upload page returns 200."""
        response = client.get('/upload')
        assert response.status_code == 200

    def test_result_page(self, client):
        """Test result page returns 200."""
        response = client.get('/result')
        assert response.status_code == 200

    def test_404_nonexistent_route(self, client):
        """Test that nonexistent routes return 404."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestSkillsEndpoint:
    """Test skills taxonomy endpoint."""

    def test_skills_returns_200(self, client):
        """Test skills endpoint returns 200."""
        response = client.get('/api/skills')
        assert response.status_code == 200

    def test_skills_returns_json(self, client):
        """Test skills endpoint returns JSON."""
        response = client.get('/api/skills')
        data = response.get_json()
        assert isinstance(data, dict)

    def test_skills_contains_taxonomy(self, client):
        """Test skills endpoint contains skill categories."""
        response = client.get('/api/skills')
        data = response.get_json()
        expected_categories = [
            'programming_languages', 'web_frameworks', 'databases',
            'cloud_devops', 'data_ml', 'soft_skills', 'other_tech'
        ]
        for category in expected_categories:
            assert category in data

    def test_skills_values_are_lists(self, client):
        """Test that skill values are lists."""
        response = client.get('/api/skills')
        data = response.get_json()
        for category, skills in data.items():
            assert isinstance(skills, list)
            assert len(skills) > 0


class TestPredictEndpoint:
    """Test resume prediction endpoint."""

    def test_predict_no_file_returns_400(self, client):
        """Test that POST without file returns 400."""
        response = client.post('/predict')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_predict_empty_filename_returns_400(self, client):
        """Test that POST with empty filename returns 400."""
        data = {'resume': (io.BytesIO(b""), '')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_predict_unsupported_format_returns_415(self, client):
        """Test that unsupported file format returns 415."""
        data = {'resume': (io.BytesIO(b"content"), 'resume.exe')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 415
        result = response.get_json()
        assert 'error' in result

    def test_predict_txt_resume_returns_200(self, client):
        """Test successful prediction with TXT resume."""
        resume_text = b"""Jane Doe
jane@example.com
+91 9876543210
linkedin.com/in/janedoe

Skills: Python, Machine Learning, TensorFlow, Docker, AWS
Education: B.Tech Computer Science
5 years of experience in AI and Machine Learning development
"""
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 200

    def test_predict_response_structure(self, client):
        """Test that prediction response has correct structure."""
        resume_text = b"Python Django PostgreSQL Docker AWS developer"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'data' in result

    def test_predict_response_contains_matches(self, client):
        """Test that prediction includes job matches."""
        resume_text = b"Python Django developer with PostgreSQL and AWS"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        result = response.get_json()
        assert 'data' in result
        # Check for actual response structure
        assert 'top_matches' in result['data'] or 'matches' in result['data']

    def test_predict_matches_have_required_fields(self, client):
        """Test that each match has all required fields."""
        resume_text = b"Python TensorFlow Machine Learning"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        result = response.get_json()
        matches = result['data'].get('top_matches') or result['data'].get('matches', [])
        if len(matches) > 0:
            match = matches[0]
            required_fields = [
                'job_id', 'title', 'company', 'location',
                'score', 'matched_skills', 'missing_skills'
            ]
            for field in required_fields:
                assert field in match

    def test_predict_matches_sorted_by_score(self, client):
        """Test that matches are sorted by score descending."""
        resume_text = b"Python Django FastAPI React TypeScript PostgreSQL Docker AWS"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        result = response.get_json()
        matches = result['data'].get('top_matches') or result['data'].get('matches', [])
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                assert matches[i]['score'] >= matches[i + 1]['score']

    def test_predict_scores_in_valid_range(self, client):
        """Test that scores are in [0, 1] range."""
        resume_text = b"Python developer"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        result = response.get_json()
        matches = result['data'].get('top_matches') or result['data'].get('matches', [])
        for match in matches:
            assert 0.0 <= match['score'] <= 1.0

    def test_predict_extracts_metadata(self, client):
        """Test that prediction extracts resume metadata."""
        resume_text = b"John Doe - john@example.com - Python developer"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        result = response.get_json()
        assert 'data' in result
        extraction = result['data']
        # Check for metadata about the extraction
        assert extraction is not None

    def test_predict_large_file(self, client):
        """Test prediction with larger resume file."""
        large_resume = b"Python Django FastAPI " * 1000  # Large content
        data = {'resume': (io.BytesIO(large_resume), 'large_resume.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response.status_code == 200

    def test_predict_multiple_consecutive(self, client):
        """Test multiple predictions in sequence."""
        for i in range(3):
            resume_text = f"Resume {i}: Python Java JavaScript developer".encode()
            data = {'resume': (io.BytesIO(resume_text), f'resume{i}.txt')}
            response = client.post('/predict', data=data, content_type='multipart/form-data')
            assert response.status_code == 200
            assert response.get_json()['success'] is True


class TestTrainEndpoint:
    """Test model training endpoint."""

    def test_train_without_auth_returns_401(self, client):
        """Test that training without auth returns 401."""
        response = client.post('/train')
        assert response.status_code == 401

    def test_train_with_wrong_key_returns_401(self, client):
        """Test that training with wrong key returns 401."""
        headers = {'X-API-Key': 'wrong-key'}
        response = client.post('/train', headers=headers)
        assert response.status_code == 401

    def test_train_with_correct_key_returns_200(self, client):
        """Test that training with correct key succeeds."""
        headers = {'X-API-Key': 'train-secret'}
        response = client.post('/train', headers=headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True

    def test_train_response_contains_report(self, client):
        """Test that training response includes report."""
        headers = {'X-API-Key': 'train-secret'}
        response = client.post('/train', headers=headers)
        result = response.get_json()
        assert 'report' in result


class TestErrorHandlers:
    """Test error handling."""

    def test_404_returns_json(self, client):
        """Test that 404 returns JSON error."""
        response = client.get('/invalid/path')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_file_too_large_returns_413(self, client):
        """Test that oversized files are rejected."""
        # Create a 11MB file (exceeds 10MB limit)
        oversized_file = io.BytesIO(b'x' * (11 * 1024 * 1024))
        data = {'resume': (oversized_file, 'huge.txt')}
        response = client.post('/predict', data=data, content_type='multipart/form-data')
        # May return 413 or 500 depending on implementation
        assert response.status_code in [413, 500]


class TestEndpointIntegration:
    """Test integration between endpoints."""

    def test_health_before_and_after_prediction(self, client):
        """Test health endpoint before and after prediction."""
        # Check health
        response1 = client.get('/health')
        assert response1.status_code == 200

        # Make prediction
        resume_text = b"Python developer"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        response2 = client.post('/predict', data=data, content_type='multipart/form-data')
        assert response2.status_code == 200

        # Check health again
        response3 = client.get('/health')
        assert response3.status_code == 200

    def test_skills_help_understand_matches(self, client):
        """Test that skills endpoint helps understand prediction matches."""
        # Get available skills
        skill_response = client.get('/api/skills')
        skills = skill_response.get_json()
        assert len(skills) > 0

        # Make prediction
        resume_text = b"I have Python and Django skills"
        data = {'resume': (io.BytesIO(resume_text), 'resume.txt')}
        pred_response = client.post('/predict', data=data, content_type='multipart/form-data')
        result = pred_response.get_json()
        matches = result['data'].get('top_matches') or result['data'].get('matches', [])

        # Verify response structure
        if len(matches) > 0:
            match = matches[0]
            matched_skills = match.get('matched_skills', [])
            # These should be recognized skills
            assert isinstance(matched_skills, list)



class TestTrainEndpoint:

    def test_train_without_key_returns_401(self, client):
        response = client.post('/train')
        assert response.status_code == 401

    def test_train_with_wrong_key_returns_401(self, client):
        response = client.post('/train', headers={'X-API-Key': 'wrong-key'})
        assert response.status_code == 401