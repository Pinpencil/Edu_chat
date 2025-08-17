from django.shortcuts import render, redirect
from .models import Class, Theme ,Team
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
import openpyxl
from django.contrib.auth import get_user_model, login
from .models import User, Post, Comment
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.utils import timezone
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.http import Http404
import os
from django.contrib.auth import get_user
import json
from django.views.decorators.http import require_http_methods
from django.conf import settings
import base64
from django.db.models import Count
from django.shortcuts import get_object_or_404
import logging

# 首页跳转视图
def home(request, custom_id=None, name=None, role=None):
    # 获取访问者IP
    ip = request.META.get('REMOTE_ADDR')
    if ip == '127.0.0.1' or ip == '::1':
        user_role = 'teacher'
        user_name = '教师'  # 本地访问者视为教师
        user_custom_id = '0'  # 本地教师的自定义ID为0
    else:
        user_role = 'student'
        user_name = '学生'
        user_custom_id = str(hash(ip))  # 使用IP哈希作为学生的自定义ID

    # 自动登录Django认证系统的用户
    User = get_user_model()
    auth_user, created = User.objects.get_or_create(
        custom_id=user_custom_id,  # 确保 custom_id 是查询条件
        defaults={
            'name': user_name,
            'role': user_role,
            'custom_id': user_custom_id,  # 设置自定义ID
        }
    )

    # 如果是新创建的用户，设置其他字段
    if created:
        auth_user.save()

    login(request, auth_user)

    themes = Theme.objects.all()  # 获取所有主题
    classes = Class.objects.all()  # 获取所有班级

    return render(request, 'home.html', {
        'user_name': user_name,
        'user_role': user_role,
        'user_custom_id': user_custom_id,
        'themes': themes,
        'classes': classes,
    })

def create_theme(request):
    classes = Class.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '').strip()
        class_id = request.POST.get('class_id')
        student_list = ''
        if class_id:
            try:
                selected_class = Class.objects.get(id=class_id)
                student_list = selected_class.student_list
            except Class.DoesNotExist:
                student_list = ''

        new_theme = Theme.objects.create(
            title=title,
            description=description,
            student_list=student_list,
        )

        # 通过 WebSocket 广播新主题信息
        broadcast_data = {
            'type': 'new_theme',
            'theme': {
                'id': new_theme.id,
                'title': new_theme.title,
                'description': new_theme.description,
                'student_list': student_list.splitlines() if student_list else [],
            }
        }
        
        # 使用 channel_layer 发送广播
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": broadcast_data
            }
        )
        
        return redirect('home', custom_id='teacher', name='教师', role='teacher')
    return render(request, 'create_theme.html', {
        'classes': classes
    })

def create_class(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        students_text = request.POST.get('students', '').strip()
        student_file = request.FILES.get('student_list')
        students = []

        # 处理Excel导入
        if student_file:
            wb = openpyxl.load_workbook(student_file)
            ws = wb.active
            for row in ws.iter_rows(min_row=1, values_only=True):
                student_name = str(row[0]).strip() if row[0] else ''
                if student_name:
                    students.append(student_name)
        # 处理手动输入
        elif students_text:
            for student_name in students_text.splitlines():
                student_name = student_name.strip()
                if student_name:
                    students.append(student_name)

        # 保存到Class模型
        student_list_str = '\n'.join(students)
        new_class = Class.objects.create(
            name=name, 
            student_list=student_list_str
        )

        # 通过 WebSocket 广播新班级信息
        broadcast_data = {
            'type': 'new_class',
            'class': {
                'id': new_class.id,
                'name': new_class.name,
                'students': students,
            }
        }
        
        # 使用 channel_layer 发送广播
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": broadcast_data
            }
        )

        return redirect('home', custom_id='teacher', name='教师', role='teacher')
    return render(request, 'create_class.html')

def enter(request, theme_id):
    theme = Theme.objects.filter(id=theme_id).first()
    theme_description = theme.description if theme.description else '无描述'

    ip = request.META.get('REMOTE_ADDR')
    user_role = 'student'
    user_name = '默认学生'
    user_custom_id = str(hash(ip))

    if not theme:
        return JsonResponse({'error': 'Theme not found'}, status=404)

    posts = Post.objects.filter(theme_id=theme_id)  # 根据 theme_id 获取帖子

    return render(request, 'enter.html', {
        'user_custom_id': user_custom_id,
        'user_name': user_name,
        'user_role': user_role,

        'theme': theme,
        'theme_id': theme_id,
        'theme_description': theme_description,
        'theme_title': theme.title,
    })

def theme_room(request, theme_id, user_name):
    print(f"Received request for theme room with theme_id: {theme_id} and user_name: {user_name}")


    theme = Theme.objects.filter(id=theme_id).first()
    if not theme:
        return JsonResponse({'error': 'Theme not found'}, status=404)

    posts = Post.objects.filter(theme_id=theme_id)  # 根据 theme_id 获取帖子
    themes = Theme.objects.all()  # 获取所有主题
    teams = Team.objects.filter(theme=theme)  # 获取当前主题下所有团队
    
    # 获取该主题下所有帖子对应的评论，并按帖子分组
    comments = {}
    for post in posts:
        comments[post.id] = Comment.objects.filter(post=post).order_by('created_at')

    # 为每个帖子添加团队信息
    posts_with_teams = []
    for post in posts:
        # 查找帖子所属的团队
        post_team = None
        for team in teams:
            if post in team.posts.all():
                post_team = team
                break
        
        # 创建一个包含团队信息的帖子对象
        post.team_info = post_team
        posts_with_teams.append(post)

    user = request.user  # 获取当前登录用户
    if not user.is_authenticated:
        print("用户未登录，重定向到首页")
        return redirect('home')  # 如果用户未登录，重定向到首页

    user_custom_id = user.custom_id
    user_role = user.role
    theme_description = theme.description if theme.description else '无描述'

    return render(request, 'theme_room.html', {
        'user_custom_id': user_custom_id,
        'user_name': user_name,
        'user_role': user_role,

        'theme_id': theme_id,
        'theme_description': theme_description,
        'theme_title': theme.title,
        'theme': theme,
        'themes': themes,  # 将所有主题传递给模板

        'teams': teams,  # 将所有团队传递给模板


        'user': user,
        'posts': posts_with_teams,
        'comments': comments,
        'data-post-username': user_name,  # 将用户名传递给模板
    })

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        # 保存图片到 media 目录，确保文件夹存在
        image_dir = 'images/'
        filename = image.name
        path = default_storage.save(os.path.join(image_dir, filename), ContentFile(image.read()))
        image_url = default_storage.url(path)
        print(f"Image uploaded successfully: {image_url}")
        # 返回图片的URL
        return JsonResponse({'image_url': image_url}, status=200)
    return JsonResponse({'error': '上传失败'}, status=400)

@csrf_exempt
def create_post(request, theme_id, user_name):
    print(f"Received request to create post for theme_id: {theme_id}")
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        print(f"Creating post with title: {title}, content: {content}, user_name: {user_name}, theme_id: {theme_id}")
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        

        # 将新创建的post与team关联
        team_id = request.POST.get('team_id')
        team = None
        
        # 验证team_id是否有效
        if team_id and team_id not in ['null', 'undefined', '']:
            try:
                team_id = int(team_id)
                team = Team.objects.filter(id=team_id).first()
            except (ValueError, TypeError):
                print(f"Invalid team_id: {team_id}")
                team = None

        user = request.user

        if user.name != user_name:
            user.name = user_name
            user.save(update_fields=['name'])

        theme = Theme.objects.filter(id=theme_id).first()
        if not theme:
            return JsonResponse({'error': 'Theme not found'}, status=404)

        if not title or not content:
            return JsonResponse({'error': 'Title and content are required'}, status=400)

        image = request.FILES.get('image')

        try:
            print(f"Creating post with data: title={title}, content={content}, user_name={user_name}, theme_id={theme_id}, theme_title={theme.title if theme else None}, image={image}")
            post = Post.objects.create(
                title=title,
                content=content,
                user_name=user_name,
                user_custom_id=user.custom_id,
                theme_id=theme_id,
                theme_title=theme.title if theme else None,
                image=image
            )
            
            # 如果有团队ID，将帖子关联到团队
            if team:
                team.posts.add(post)
                team.save()
                print(f"Post {post.id} associated with team {team.name}")
            
            return JsonResponse({'id': post.id})
        except Exception as e:
            print(f"Error creating post: {str(e)}")
            return JsonResponse({'error': f'Failed to create post: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def add_comment(request, post_id, user_name):
    try:
        data = json.loads(request.body)
        content = data.get('content')

        # 查询数据库中的 Post 和 User 对象
        post = Post.objects.get(id=post_id)
        user = User.objects.filter(name=user_name).first()
        if not user:
            return JsonResponse({'error': '用户不存在'}, status=404)

        # 创建评论对象并保存
        comment = Comment.objects.create(post=post, user=user, content=content)
        print(f"Comment created: {comment.id} by {user.name}")

        # 返回成功响应
        return JsonResponse({
            'message': '评论已保存',
            'comment_id': comment.id,
            'user_name': user.name,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, status=201)

    except Post.DoesNotExist:
        return JsonResponse({'error': '帖子不存在'}, status=404)
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        return JsonResponse({'error': f'添加评论失败: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_post(request, post_id):
    print(f"Received request to delete post with ID: {post_id}")
    try:
        post = Post.objects.get(id=post_id)
        post.delete()

        # 通过 WebSocket 广播删除帖子信息
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": {
                    "type": "delete_post",
                    "post_id": post_id
                }
            }
        )

        return JsonResponse({"message": "帖子已删除"}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({"error": "帖子不存在"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"删除帖子失败: {str(e)}"}, status=500)

@csrf_exempt
def toggle_like(request, post_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            liked = data.get('liked', False)
            user = request.user
            
            # 添加调试日志
            print(f"toggle_like called with post_id={post_id}, liked={liked}, user={user}")

            post = Post.objects.get(id=post_id)

            # 检查 liked_users 字段是否存在
            if not hasattr(post, 'liked_users'):
                print("Error: 'liked_users' field is missing in Post model")
                return JsonResponse({'status': 'error', 'message': "'liked_users' field is missing in Post model"}, status=500)

            # 将当前用户添加到 liked_users
            if liked:
                post.liked_users.add(user)
            else:
                post.liked_users.remove(user)

            # 确保 likes 字段不小于 0
            if not liked and post.likes > 0:
                post.likes -= 1
            elif liked:
                post.likes += 1

            post.save()

            return JsonResponse({'status': 'success', 'likes': post.likes})
        except Post.DoesNotExist:
            print(f"Error: Post with id {post_id} does not exist")
            return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
        except Exception as e:
            print(f"Error in toggle_like: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_theme(request, theme_id):
    print(f"Received request to delete theme with ID: {theme_id}")
    try:
        theme = Theme.objects.get(id=theme_id)
        theme.delete()

        # 通过 WebSocket 广播删除主题信息
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": {
                    "type": "delete_theme",
                    "theme_id": theme_id
                }
            }
        )

        return JsonResponse({"message": "主题已删除"}, status=200)
    except Theme.DoesNotExist:
        return JsonResponse({"error": "主题不存在"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"删除主题失败: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_class(request, class_id):
    try:
        class_instance = Class.objects.get(id=class_id)
        class_instance.delete()

        # 通过 WebSocket 广播删除班级信息
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": {
                    "type": "delete_class",
                    "class_id": class_id
                }
            }
        )

        return JsonResponse({"message": "班级已删除"}, status=200)
    except Class.DoesNotExist:
        return JsonResponse({"error": "班级不存在"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"删除班级失败: {str(e)}"}, status=500)

@csrf_exempt
def update_post(request, post_id):
    if request.method == 'POST':
        try:
            # 获取帖子对象
            post = Post.objects.get(id=post_id)

            # 解析请求数据
            data = json.loads(request.body)
            new_title = data.get('title', '').strip()
            new_content = data.get('content', '').strip()
            new_image_url = data.get('image', '').strip()

            # 更新标题和内容
            post.title = new_title
            post.content = new_content
            # 如果有新的图片URL（base64或文件名），则处理图片保存到 media/images
            if new_image_url:

                # 判断是否为 base64 格式
                if new_image_url.startswith('data:image'):
                    format, imgstr = new_image_url.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data = base64.b64decode(imgstr)
                    filename = f'post_{post_id}.{ext}'
                    image_path = os.path.join('images', filename)
                    post.image.save(image_path, ContentFile(img_data), save=False)
                else:
                    # 如果是文件名或相对路径，直接赋值
                    post.image = os.path.join('images', os.path.basename(new_image_url))
            
            print(f"Updating post {post_id}: title={new_title}, content={new_content}, image={new_image_url}")

            # 保存更新后的帖子
            post.save()

            # 通过 WebSocket 广播帖子更新信息
            channel_layer = get_channel_layer()
            broadcast_data = {
                "type": "update_post",
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "image": str(post.image) if post.image else "",
                }
            }
            async_to_sync(channel_layer.group_send)(
                "broadcast_group",
                {
                    "type": "broadcast_message",
                    "message": broadcast_data
                }
            )

            return JsonResponse({'success': True, 'message': 'Post updated successfully'})
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Post not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def theme_stats(request, theme_id):
    # 获取主题对象或返回404
    theme = get_object_or_404(Theme, id=theme_id)
    themes = Theme.objects.all()  # 获取所有主题
    # 查询该主题下的所有帖子
    posts = Post.objects.filter(theme_id=theme_id)

    # 统计数据
    total_posts = posts.count()
    total_posters = posts.values('user_name').distinct().count()
    # 前三发帖用户
    top_posters_qs = posts.values('user_name').annotate(count=Count('id')).order_by('-count')[:3]
    top_posters = [(item['user_name'], item['count']) for item in top_posters_qs]

    # 评论最多的帖子和点赞最多的帖子
    most_commented_post = posts.annotate(num_comments=Count('comments')).order_by('-num_comments').first()
    most_liked_post = posts.order_by('-likes').first()

    # 高亮显示次数最多的帖子
    highlighted_posts = posts.filter(showed_times__gt=0).order_by('-showed_times')
    highlighted_post = highlighted_posts.first() if highlighted_posts.exists() else None

    return render(request, 'statistics.html', {
        'theme': theme,
        'themes': themes,  # 将所有主题传递给模板
        'theme_id': theme_id,
        'user': request.user,
        'user_name': getattr(request.user, 'name', '未登录用户'),
        'user_role': getattr(request.user, 'role', ''),
        'total_posts': total_posts,
        'total_posters': total_posters,
        'top_posters': top_posters,
        'most_commented_post': most_commented_post or None,
        'most_liked_post': most_liked_post or None,
        'highlighted_posts': highlighted_posts,
        'highlighted_post': highlighted_post,
    })

@csrf_exempt 
def highlight_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            
            # 首先清除同一主题下所有帖子的高亮状态
            Post.objects.filter(theme_id=post.theme_id).update(is_highlighted=False)
            print(f"Cleared highlight status for all posts in theme {post.theme_id}")
            
            # 设置当前帖子为高亮状态并增加显示次数
            post.showed_times += 1
            post.is_highlighted = True
            post.save()
            
            print(f"Post {post.id} highlighted successfully! Showed times: {post.showed_times}")

            return JsonResponse({'status': 'success', 'showed_times': post.showed_times})
        except Post.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def create_team(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('team_name')
            description = request.POST.get('team_description', '').strip()
            theme_id = request.POST.get('theme_id')
            
            if not title:
                return JsonResponse({'error': '团队名称不能为空'}, status=400)
            
            print(f"Creating team with title: {title}, description: {description}, theme_id: {theme_id}")
            
            # 创建团队
            new_team = Team.objects.create(
                name=title,
                description=description,
                theme=Theme.objects.get(id=theme_id) if theme_id else None,
                members=""  # 初始化为空字符串
            )
            
            # 通过 WebSocket 广播团队创建信息
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "broadcast_group",
                {
                    "type": "broadcast_message",
                    "message": {
                        "type": "create_team",
                        "team_id": new_team.id,
                        "team_name": new_team.name,
                        "team_description": new_team.description,
                        "member_count": new_team.get_member_count(),
                        "theme_id": theme_id
                    }
                }
            )
            
            return JsonResponse({
                'id': new_team.id, 
                'name': new_team.name,
                'description': new_team.description,
                'member_count': new_team.get_member_count()
            }, status=200)
            
        except Theme.DoesNotExist:
            return JsonResponse({'error': '主题不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'创建团队失败: {str(e)}'}, status=500)
    
    return JsonResponse({'error': '无效的请求方法'}, status=400)

@csrf_exempt
def delete_team(request, team_id):
    if request.method == 'POST':
        try:
            team = Team.objects.get(id=team_id)
            team_data = {
                "id": team.id,
                "name": team.name,
                "theme_id": team.theme.id if team.theme else None
            }
            
            team.delete()
            
            # 通过 WebSocket 广播团队删除信息
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "broadcast_group",
                {
                    "type": "broadcast_message",
                    "message": {
                        "type": "delete_team",
                        "team_id": team_id,
                        "team": team_data
                    }
                }
            )
            
            return JsonResponse({'status': 'success', 'message': '团队删除成功'}, status=200)
            
        except Team.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '团队不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'删除团队失败: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '无效的请求方法'}, status=400)

@csrf_exempt
def join_team(request, team_id, user_name):
    if request.method == 'POST':
        try:
            # 获取团队对象
            team = Team.objects.filter(id=team_id).first()
            if not team:
                return JsonResponse({'success': False, 'error': 'Team not found'}, status=404)
            
            # 检查用户是否已经在该团队中
            current_members = team.members.splitlines() if team.members else []
            if user_name not in current_members:
                # 添加用户到团队成员列表
                if team.members:
                    team.members += f"\n{user_name}"
                else:
                    team.members = user_name
                team.save()
            
            # 从其他团队中移除该用户
            other_teams = Team.objects.filter(theme=team.theme).exclude(id=team_id)
            for other_team in other_teams:
                if other_team.members:
                    members_list = other_team.members.splitlines()
                    if user_name in members_list:
                        members_list.remove(user_name)
                        other_team.members = '\n'.join(members_list)
                        other_team.save()
            
            return JsonResponse({'success': True, 'message': 'Successfully joined team'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_team_posts(request, team_id):
    """获取指定团队的帖子"""
    try:
        # 获取团队对象
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return JsonResponse({'success': False, 'error': 'Team not found'}, status=404)
        
        # 获取该团队关联的所有帖子
        posts = team.posts.all().order_by('-created_at')
        
        # 构建帖子数据
        posts_data = []
        for post in posts:
            # 获取帖子的评论
            comments = Comment.objects.filter(post=post).order_by('created_at')
            comments_data = [
                {
                    'user_name': comment.user.name,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat()
                }
                for comment in comments
            ]
            
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'user_name': post.user_name,
                'created_at': post.created_at.isoformat(),
                'likes': post.likes,
                'comment_count': comments.count(),
                'comments': comments_data,
                'image_url': post.image.url if post.image else None,
                'team_name': team.name,  # 添加团队名称
            }
            posts_data.append(post_data)
        
        return JsonResponse({
            'success': True,
            'posts': posts_data,
            'team_name': team.name
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    if request.method == 'POST':
        try:
            team = Team.objects.get(id=team_id)
            
            # 检查用户是否已经在该团队中
            current_members = [name.strip() for name in team.members.splitlines() if name.strip()]
            if user_name in current_members:
                return JsonResponse({'status': 'error', 'message': '用户已在该团队中'}, status=400)
            
            # 将用户添加到团队成员列表
            if team.members:
                team.members += f"\n{user_name}"
            else:
                team.members = user_name
            
            # 去除其他队伍中的此成员
            other_teams = Team.objects.exclude(id=team_id)
            for other_team in other_teams:
                other_members = [name.strip() for name in other_team.members.splitlines() if name.strip()]
                if user_name in other_members:
                    # 从其他团队中移除该用户
                    updated_members = [name for name in other_members if name != user_name]
                    other_team.members = '\n'.join(updated_members)
                    other_team.save()
                    print(f"Removed user {user_name} from team {other_team.name}")
            
            team.save()

            # 通过 WebSocket 广播用户加入团队信息
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "broadcast_group",
                {
                    "type": "broadcast_message",
                    "message": {
                        "type": "join_team",
                        "team_id": team_id,
                        "user_name": user_name,
                        "member_count": team.get_member_count()
                    }
                }
            )

            return JsonResponse({
                'status': 'success', 
                'message': '用户成功加入团队',
                'member_count': team.get_member_count()
            }, status=200)
            
        except Team.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '团队不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'加入团队失败: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '无效的请求方法'}, status=400)

@csrf_exempt
def get_all_posts(request, theme_id):
    """获取指定主题的所有帖子"""
    try:
        # 获取主题对象
        theme = Theme.objects.filter(id=theme_id).first()
        if not theme:
            return JsonResponse({'success': False, 'error': 'Theme not found'}, status=404)
        
        # 获取该主题下的所有帖子
        posts = Post.objects.filter(theme_id=theme_id).order_by('-created_at')
        
        # 构建帖子数据
        posts_data = []
        for post in posts:
            # 获取帖子的评论
            comments = Comment.objects.filter(post=post).order_by('created_at')
            comments_data = [
                {
                    'user_name': comment.user.name,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat()
                }
                for comment in comments
            ]
            
            # 查找帖子所属的团队
            post_team = None
            teams = Team.objects.filter(theme=theme)
            for team in teams:
                if post in team.posts.all():
                    post_team = team
                    break
            
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'user_name': post.user_name,
                'created_at': post.created_at.isoformat(),
                'likes': post.likes,
                'comment_count': comments.count(),
                'comments': comments_data,
                'image_url': post.image.url if post.image else None,
                'team_name': post_team.name if post_team else None,
                'is_highlighted': post.is_highlighted,  # 添加高亮状态
            }
            posts_data.append(post_data)
        
        return JsonResponse({
            'success': True,
            'posts': posts_data,
            'theme_title': theme.title
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def get_highlighted_posts(request, theme_id):
    """获取指定主题下当前高亮的帖子"""
    try:
        # 获取主题对象
        theme = Theme.objects.filter(id=theme_id).first()
        if not theme:
            return JsonResponse({'success': False, 'error': 'Theme not found'}, status=404)
        
        print(f"Fetching highlighted posts for theme_id: {theme_id}")
        
        # 获取该主题下所有高亮的帖子
        highlighted_posts = Post.objects.filter(theme_id=theme_id, is_highlighted=True)
        print(f"Found {highlighted_posts.count()} highlighted posts in theme {theme_id}")
        
        # 构建高亮帖子的ID列表
        highlighted_post_ids = [post.id for post in highlighted_posts]
        print(f"Highlighted post IDs: {highlighted_post_ids}")
        
        # 构建高亮帖子的完整信息
        highlighted_posts_data = []
        for post in highlighted_posts:
            # 获取帖子的评论
            comments = Comment.objects.filter(post=post).order_by('created_at')
            comments_data = [
                {
                    'user_name': comment.user.name,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat()
                }
                for comment in comments
            ]
            
            # 查找帖子所属的团队
            post_team = None
            teams = Team.objects.filter(theme_id=theme_id)
            for team in teams:
                if post in team.posts.all():
                    post_team = team
                    break
            
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'user_name': post.user_name,
                'created_at': post.created_at.isoformat(),
                'likes': post.likes,
                'comment_count': comments.count(),
                'comments': comments_data,
                'image_url': post.image.url if post.image else None,
                'team_name': post_team.name if post_team else None,
                'is_highlighted': post.is_highlighted,
                'showed_times': post.showed_times,
            }
            highlighted_posts_data.append(post_data)
        
        response_data = {
            'success': True,
            'highlighted_post_ids': highlighted_post_ids,
            'highlighted_posts': highlighted_posts_data,
            'count': len(highlighted_post_ids)
        }
        print(f"Returning response with {len(highlighted_posts_data)} highlighted posts")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def get_post_detail(request, post_id):
    """获取单个帖子的详细信息"""
    try:
        post = Post.objects.filter(id=post_id).first()
        if not post:
            return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)
        
        print(f"Fetching post detail for post_id: {post_id}")
        
        # 获取帖子的评论
        comments = Comment.objects.filter(post=post).order_by('created_at')
        comments_data = [
            {
                'user_name': comment.user.name,
                'content': comment.content,
                'created_at': comment.created_at.isoformat()
            }
            for comment in comments
        ]
        
        # 查找帖子所属的团队
        post_team = None
        teams = Team.objects.filter(theme_id=post.theme_id)
        for team in teams:
            if post in team.posts.all():
                post_team = team
                break
        
        post_data = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'user_name': post.user_name,
            'created_at': post.created_at.isoformat(),
            'likes': post.likes,
            'comment_count': comments.count(),
            'comments': comments_data,
            'image_url': post.image.url if post.image else None,
            'team_name': post_team.name if post_team else None,
            'is_highlighted': post.is_highlighted,
            'showed_times': post.showed_times,
        }
        
        return JsonResponse({
            'success': True,
            'post': post_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
