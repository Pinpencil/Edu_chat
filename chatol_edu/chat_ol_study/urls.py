"""chat_ol_study URL Configuration
URL Patterns:
1. path('admin/', admin.site.urls)
    - 管理后台的URL路由,访问/admin/时进入Django自带的管理后台。
2. path('', views.home, name='home')
    - 网站首页的URL路由,访问根路径时调用views.home视图函数。
3. path('home/<str:custom_id>/<str:name>/', views.home, name='home')
    - 动态路由,带有custom_id和name参数,访问/home/自定义ID/用户名/时调用views.home视图函数。

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chat_ol_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home_index'),  # 根路径指向 home 视图
    path('admin/', admin.site.urls),  # 管理后台
    path('home/<str:custom_id>/<str:name>/<str:role>/', views.home, name='home'),
    
    path('create_theme/', views.create_theme, name='create_theme'),  # 新增创建主题的路由
    path('create_class/', views.create_class, name='create_class'),  # 新增创建班级的路由

    path('theme_room/<int:theme_id>/<str:user_name>/', views.theme_room, name='theme_room'),  # 主题房间路由
    path('enter/<int:theme_id>/', views.enter, name='enter'),  # 进入房间路由

    path('create_post/<int:theme_id>/<str:user_name>/', views.create_post, name='create_post'),  # 新增创建帖子路由
    path('theme_room/upload_image/', views.upload_image, name='upload_image'),

    path('add_comment/<int:post_id>/<str:user_name>/', views.add_comment, name='add_comment'),  # 添加评论路由
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('toggle_like/<int:post_id>/', views.toggle_like, name='toggle_like'),

    path('delete_theme/<int:theme_id>/', views.delete_theme, name='delete_theme'),
    path('delete_class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('update_post/<int:post_id>/', views.update_post, name='update_post'),
    path('highlight_post/<int:post_id>/', views.highlight_post, name='highlight_post'),

    path('create_team/', views.create_team, name='create_team'),  # 创建团队路由
    path('delete_team/<int:team_id>/', views.delete_team, name='delete_team'),  # 删除团队路由
    path('join_team/<int:team_id>/<str:user_name>/', views.join_team, name='join_team'),  # 加入团队路由
    path('get_team_posts/<int:team_id>/', views.get_team_posts, name='get_team_posts'),  # 获取团队帖子路由
    path('get_all_posts/<int:theme_id>/', views.get_all_posts, name='get_all_posts'),  # 获取所有帖子路由
    path('get_highlighted_posts/<int:theme_id>/', views.get_highlighted_posts, name='get_highlighted_posts'),  # 获取高亮帖子路由
    path('get_post_detail/<int:post_id>/', views.get_post_detail, name='get_post_detail'),  # 获取单个帖子详情路由
    path('theme_stats/<int:theme_id>/', views.theme_stats, name='theme_stats'),  # 主题统计路由


    path('chat_ol_app/', include('chat_ol_app.urls')),  # 包含子应用的路由

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
