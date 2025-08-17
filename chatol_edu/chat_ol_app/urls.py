from django.urls import path
from . import views

urlpatterns = [
    path('theme_room/upload_image/', views.upload_image, name='upload_image'),
    
    path('create_post/<int:theme_id>/<str:user_name>/', views.create_post, name='create_post'),
    path('add_comment/<int:post_id>/<str:user_name>/', views.add_comment, name='add_comment'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('toggle_like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('update_post/<int:post_id>/', views.update_post, name='update_post'),
    path('highlight_post/<int:post_id>/', views.highlight_post, name='highlight_post'),
    
    path('delete_theme/<int:theme_id>/', views.delete_theme, name='delete_theme'),
    path('delete_class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('theme_stats/<int:theme_id>/', views.theme_stats, name='theme_stats'),
    
    path('create_team/', views.create_team, name='create_team'),
    path('delete_team/<int:team_id>/', views.delete_team, name='delete_team'),
    path('join_team/<int:team_id>/<str:user_name>/', views.join_team, name='join_team'),
    path('get_team_posts/<int:team_id>/', views.get_team_posts, name='get_team_posts'),
    path('get_all_posts/<int:theme_id>/', views.get_all_posts, name='get_all_posts'),
    path('get_highlighted_posts/<int:theme_id>/', views.get_highlighted_posts, name='get_highlighted_posts'),
]