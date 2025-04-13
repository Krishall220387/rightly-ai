from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_document, name='upload_document'),
    path('manage-documents/', views.manage_documents, name='manage_documents'),
    path('delete-document/<int:document_id>/', views.delete_document, name='delete_document'),
    path('create-blog/', views.create_blog, name='create_blog'),
    path('edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('update-blog/<int:blog_id>/', views.update_blog, name='update_blog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('download-blog/<int:blog_id>/', views.download_blog, name='download_blog'),
    path('check-grammar/', views.check_grammar_view, name='check_grammar'),
] 