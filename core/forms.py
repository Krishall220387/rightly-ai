from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Document, Blog

# Define allowed content types for document uploads
ALLOWED_CONTENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration that extends UserCreationForm with email field.
    """
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class DocumentUploadForm(forms.ModelForm):
    """
    Form for uploading documents with title and file fields.
    Includes validation for file types and size.
    """
    class Meta:
        model = Document
        fields = ('title', 'file')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        """
        Validate the uploaded file's type and size.
        
        Returns:
            The cleaned file data if validation passes
            
        Raises:
            forms.ValidationError: If file type is not allowed or size exceeds limit
        """
        file = self.cleaned_data.get('file')
        if file:
            # Check file type
            if file.content_type not in ALLOWED_CONTENT_TYPES:
                raise forms.ValidationError(
                    "Unsupported file type. Allowed types: PDF, DOC, DOCX."
                )
            
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    "File size too large. Maximum size is 10MB."
                )
        return file

class BlogCreationForm(forms.ModelForm):
    """
    Form for creating new blog posts with topic, tone, and keyword fields.
    """
    user_keywords = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter keywords separated by commas",
        required=True
    )
    
    tone = forms.ChoiceField(
        choices=[
            ('professional', 'Professional'),
            ('casual', 'Casual'),
            ('friendly', 'Friendly'),
            ('academic', 'Academic')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = Blog
        fields = ('topic', 'user_keywords', 'tone')
        widgets = {
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_user_keywords(self):
        """
        Convert comma-separated keywords into a JSON list.
        """
        keywords = self.cleaned_data.get('user_keywords', '')
        if keywords:
            # Split by comma and strip whitespace
            keyword_list = [k.strip() for k in keywords.split(',')]
            # Remove empty strings
            keyword_list = [k for k in keyword_list if k]
            return keyword_list
        return [] 