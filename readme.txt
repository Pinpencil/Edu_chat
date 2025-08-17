安装须知

注意 确保chatol edu文件夹的路径中没有中文
==========================================================
安装流程

启用chat_edu下的install批处理文件进行一键安装
==========================================================
安装问题解决

（大部分报错信息会在install批处理文件运行时抛出）
若在安装python时出现版本报错问题，或者在导入依赖包时出现问题：
	点击chat_edu下的python-3.8.0-amd64
	进行repair，然后再uninstall
==========================================================
主要操作：
1，登入教师主页，浏览器访问
	localhost:8001
	
2，登入学生页面，浏览器访问
	（此处替换为本机ipv4地址）：8001
	
3，删除所有数据（清除数据库）
	删除chatol_edu下的db.sqlite3文件
	删除chatol_edu/chat_ol_app/migrations下的0001_initial文件
	删除chatol_edu/media下的所有图片或文档文件（不要删文件夹）
	win+r输入cmd点确认打开命令行
	依次运行以下命令
	cd （替换为到chatol_edu的文件路径）
	.\.venv\Scripts\activate
	python manage.py makemigrations chat_ol_app
	python manage.py migrate
     再启动服务器即可
	
	