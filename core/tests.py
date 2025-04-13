from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile, TemporaryUploadedFile
from django.db import transaction
from django.conf import settings
from .models import Blog, Document
from unittest.mock import patch, MagicMock
import json
import os
import concurrent.futures
import time
from django.core.cache import cache

# Create your tests here.

class AuthenticationTests(TestCase):
    """Tests for user authentication functionality"""
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        self.login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

    def test_signup(self):
        """Test successful user signup"""
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_signup_duplicate_username(self):
        """Test signup with duplicate username"""
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists')

    def test_login(self):
        """Test successful user login"""
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(reverse('login'), self.login_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

class DocumentTests(TestCase):
    """Tests for document upload and management"""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        # Create test files
        self.valid_file = SimpleUploadedFile(
            "test.txt",
            b"Test document content",
            content_type="text/plain"
        )
        self.large_file = SimpleUploadedFile(
            "large.txt",
            b"x" * (settings.MAX_UPLOAD_SIZE + 1),
            content_type="text/plain"
        )
        self.invalid_file = SimpleUploadedFile(
            "test.exe",
            b"malicious content",
            content_type="application/x-msdownload"
        )

    def test_document_upload(self):
        """Test successful document upload"""
        response = self.client.post(reverse('upload_document'), {
            'title': 'Test Document',
            'file': self.valid_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Document.objects.filter(title='Test Document').exists())

    def test_document_upload_large_file(self):
        """Test document upload with file exceeding size limit"""
        response = self.client.post(reverse('upload_document'), {
            'title': 'Large Document',
            'file': self.large_file
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(title='Large Document').exists())
        self.assertContains(response, 'File size exceeds limit')

    def test_document_upload_invalid_format(self):
        """Test document upload with invalid file format"""
        response = self.client.post(reverse('upload_document'), {
            'title': 'Invalid Document',
            'file': self.invalid_file
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(title='Invalid Document').exists())
        self.assertContains(response, 'Invalid file format')

    def test_document_cleanup(self):
        """Test cleanup of temporary files after upload"""
        with transaction.atomic():
            doc = Document.objects.create(
                user=self.user,
                title='Test Document',
                file=self.valid_file
            )
            file_path = doc.file.path
            self.assertTrue(os.path.exists(file_path))
        
        # Simulate error during processing
        with self.assertRaises(Exception):
            raise Exception("Simulated error")
        
        # Verify file is cleaned up
        self.assertFalse(os.path.exists(file_path))

class BlogTests(TransactionTestCase):
    """Tests for blog creation, generation, and editing"""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        # Create test document
        self.test_file = SimpleUploadedFile(
            "test.txt",
            b"Test document content",
            content_type="text/plain"
        )
        self.document = Document.objects.create(
            user=self.user,
            title='Test Document',
            file=self.test_file
        )

    def test_blog_creation_invalid_data(self):
        """Test blog creation with invalid input data"""
        test_cases = [
            {
                'data': {'blog_title': '', 'user_keywords': 'test', 'topic': 'Test'},
                'error': 'Blog title is required'
            },
            {
                'data': {'blog_title': 'Test', 'user_keywords': '', 'topic': 'Test'},
                'error': 'Keywords are required'
            },
            {
                'data': {'blog_title': 'Test', 'user_keywords': 'test', 'topic': ''},
                'error': 'Topic is required'
            }
        ]
        
        for case in test_cases:
            response = self.client.post(reverse('create_blog'), case['data'])
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, case['error'])

    @patch('openai.ChatCompletion.create')
    def test_blog_generation_api_errors(self, mock_openai):
        """Test blog generation with various API error scenarios"""
        blog = Blog.objects.create(
            user=self.user,
            blog_title='Test Blog',
            user_keywords=['test', 'blog'],
            topic='Test Topic'
        )
        
        # Test cases for different API errors
        error_cases = [
            (Exception("API Timeout"), "API request timed out"),
            (Exception("Invalid API Key"), "Invalid API key"),
            (Exception("Malformed Response"), "Invalid API response")
        ]
        
        for error, expected_message in error_cases:
            mock_openai.side_effect = error
            response = self.client.post(reverse('generate_blog'), json.dumps({
                'blog_id': blog.id,
                'document_ids': [self.document.id]
            }), content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertFalse(data['success'])
            self.assertIn(expected_message, data['error'])

    def test_concurrent_blog_generation(self):
        """Test handling of concurrent blog generation requests"""
        blog = Blog.objects.create(
            user=self.user,
            blog_title='Test Blog',
            user_keywords=['test', 'blog'],
            topic='Test Topic'
        )
        
        def generate_blog():
            return self.client.post(reverse('generate_blog'), json.dumps({
                'blog_id': blog.id,
                'document_ids': [self.document.id]
            }), content_type='application/json')
        
        # Simulate concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_blog) for _ in range(5)]
            responses = [f.result() for f in futures]
        
        # Verify responses
        success_count = sum(1 for r in responses if json.loads(r.content)['success'])
        self.assertEqual(success_count, 1)  # Only one request should succeed

    def test_performance_benchmark(self):
        """Test blog generation performance"""
        blog = Blog.objects.create(
            user=self.user,
            blog_title='Test Blog',
            user_keywords=['test', 'blog'],
            topic='Test Topic'
        )
        
        start_time = time.time()
        response = self.client.post(reverse('generate_blog'), json.dumps({
            'blog_id': blog.id,
            'document_ids': [self.document.id]
        }), content_type='application/json')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 30)  # Should complete within 30 seconds

class IntegrationTests(TestCase):
    """End-to-end integration tests"""
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_full_user_flow(self):
        """Test complete user flow from signup to blog download"""
        # Signup
        self.client.post(reverse('signup'), self.user_data)
        
        # Login
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Create blog
        response = self.client.post(reverse('create_blog'), {
            'blog_title': 'Integration Test Blog',
            'user_keywords': 'test, integration',
            'topic': 'Integration Testing'
        })
        self.assertEqual(response.status_code, 200)
        blog = Blog.objects.get(blog_title='Integration Test Blog')
        
        # Generate blog
        response = self.client.post(reverse('generate_blog'), json.dumps({
            'blog_id': blog.id,
            'document_ids': []
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Edit blog
        response = self.client.post(reverse('update_blog', args=[blog.id]), {
            'blog_title': 'Updated Integration Blog',
            'blog_outline': 'Updated Outline',
            'blog_draft': 'Updated Draft'
        })
        self.assertEqual(response.status_code, 200)
        
        # Download blog
        response = self.client.get(reverse('download_blog', args=[blog.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    def tearDown(self):
        """Cleanup after tests"""
        # Clear cache
        cache.clear()
        
        # Remove temporary files
        for doc in Document.objects.all():
            if os.path.exists(doc.file.path):
                os.remove(doc.file.path)
