from django.db import models
from django.core.validators import FileExtensionValidator

# 用户模型
class User(models.Model):
    ROLE_CHOICES = [
        ('teacher', '教师'),
        ('student', '学生'),
    ]
    REQUIRED_FIELDS = ['name']  # 确保name字段是必填的
    USERNAME_FIELD = 'custom_id'  # 使用自定义ID作为用户名字段

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    custom_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # 自定义 ID

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

# 主题模型
class Theme(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    class_name = models.TextField(blank=True, verbose_name="班级")
    student_list = models.TextField(blank=True, verbose_name="学生名单")
    created_at = models.DateTimeField(auto_now_add=True)

# 帖子模型
class Post(models.Model):
    user_name = models.CharField(max_length=100)  # 保留用户名称
    user_custom_id = models.CharField(max_length=255, null=True, blank=True)  # 自定义用户 ID

    theme_id = models.IntegerField(default=0)  # 使用整数字段存储主题 ID，默认值为 0
    theme_title = models.CharField(max_length=200, null=True, blank=True)  # 可选存储主题标题

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    document = models.FileField(upload_to='documents/', blank=True, null=True)

    likes = models.PositiveIntegerField(default=0)
    liked_users = models.ManyToManyField('User', related_name='liked_posts', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    showed_times = models.PositiveIntegerField(default=0)  # 显示次数

    is_highlighted = models.BooleanField(default=False)  # 是否高亮显示

# 评论模型
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} 评论: {self.content[:20]}"


# 班级模型
class Class(models.Model):
    name = models.CharField(max_length=100, verbose_name="班级名称")
    student_list = models.TextField(blank=True, verbose_name="学生名单")  # 用TextField替代JSONField
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def get_students(self):
        """返回学生名单列表，过滤空行"""
        return [name.strip() for name in self.student_list.splitlines() if name.strip()]
    
    def get_student_count(self):
        """返回学生数量"""
        return len(self.get_students())

    def __str__(self):
        return self.name
    
class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="团队名称")
    description = models.TextField(blank=True, verbose_name="团队描述")
    members = models.TextField(blank=True, verbose_name="团队成员")  # 用TextField存储成员字符串列表
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='teams', verbose_name="所属主题")

    posts = models.ManyToManyField(Post, related_name='teams', blank=True, verbose_name="关联帖子")

    def __str__(self):
        return self.name

    def get_member_count(self):
        """返回团队成员数量"""
        if not self.members:
            return 0
        # 按行分割成员列表，过滤空行，返回数量
        return len([name.strip() for name in self.members.splitlines() if name.strip()])
