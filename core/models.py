from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.utils.text import slugify
import os

def document_upload_path(instance, filename):
    """
    Generate upload path for document files.
    
    Args:
        instance: The Document instance
        filename: Original filename
        
    Returns:
        str: Path where the file should be stored
    """
    # Create a clean filename
    ext = filename.split('.')[-1]
    clean_filename = f"{instance.title.lower().replace(' ', '_') if instance.title else filename}"
    # Return path with user-specific directory
    return os.path.join('documents', f'user_{instance.user.id}', clean_filename)

class Document(models.Model):
    """
    Model representing a document uploaded by a user.
    
    Attributes:
        user (ForeignKey): The user who uploaded the document
        file (FileField): The actual document file
        title (CharField): Optional title for the document
        uploaded_at (DateTimeField): Timestamp of when the document was uploaded
        file_type (CharField): Type of the document (PDF, DOC, etc.)
        file_size (IntegerField): Size of the file in bytes
        processed_content (TextField): Extracted text content from the document
        word_count (IntegerField): Number of words in the document
        status (CharField): Processing status of the document
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=10, blank=True)
    file_size = models.IntegerField(default=0)
    processed_content = models.TextField(blank=True)
    word_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        """Return string representation of the document."""
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save method to set file type and size.
        
        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        if self.file:
            # Set file type
            self.file_type = self.file.name.split('.')[-1].lower()
            # Set file size
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete method to remove the file from storage.
        
        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def get_file_extension(self):
        """
        Get the file extension of the document.
        
        Returns:
            str: File extension in lowercase
        """
        return self.file_type

    def get_file_size_mb(self):
        """
        Get the file size in megabytes.
        
        Returns:
            float: File size in megabytes
        """
        return round(self.file_size / (1024 * 1024), 2)

    def get_word_count(self):
        """
        Calculate and return the word count of the processed content.
        
        Returns:
            int: Number of words in the document
        """
        if self.processed_content:
            return len(self.processed_content.split())
        return 0

    def update_status(self, status):
        """
        Update the processing status of the document.
        
        Args:
            status (str): New status value
            
        Raises:
            ValueError: If status is not in STATUS_CHOICES
        """
        if status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {status}")
        self.status = status
        self.save()

class Blog(models.Model):
    """
    Model representing generated blog posts.
    
    Attributes:
        user (ForeignKey): User who created the blog
        topic (CharField): Main topic/title of the blog
        target_keywords (JSONField): Keywords provided by user
        additional_keywords (JSONField): AI-suggested keywords
        tone (CharField): Writing tone for the blog
        blog_title (CharField): Title of the blog
        blog_outline (TextField): Generated blog outline
        blog_draft (TextField): Generated blog content
        created_at (DateTimeField): Creation timestamp
        updated_at (DateTimeField): Last update timestamp
        reference_documents (ManyToManyField): Documents referenced in the blog
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_title = models.CharField(max_length=255, blank=True)
    topic = models.CharField(max_length=255)
    tone = models.CharField(max_length=50, default='professional')
    target_keywords = models.JSONField(default=list)
    additional_keywords = models.JSONField(default=list)
    blog_outline = models.JSONField(null=True, blank=True)
    blog_draft = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reference_documents = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return self.blog_title or self.topic

    def save(self, *args, **kwargs):
        """
        Override save method to update timestamps.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().save(*args, **kwargs)

    def update_seo_score(self):
        """
        Calculate and update SEO score based on content analysis.
        
        Returns:
            int: Updated SEO score
        """
        # Implement SEO scoring logic here
        self.seo_score = 0  # Placeholder
        self.save()
        return self.seo_score

    class Meta:
        ordering = ['-created_at']
