// 页面加载和进场动画控制
document.addEventListener('DOMContentLoaded', function() {
    // 页面加载完成后添加loaded类
    document.body.classList.add('loaded');
    
    // 设置进场动画顺序
    setTimeout(() => {
        document.querySelector('.theme-header').classList.add('visible');
        
        // 标题闪光效果
        const title = document.querySelector('.theme-header h1');
        title.classList.add('title-highlight');
        
        setTimeout(() => {
            // 用户信息面板显示
            const userInfoPanel = document.querySelector('.user-info-panel');
            if (userInfoPanel) userInfoPanel.classList.add('visible');
            
            setTimeout(() => {
                // 发布帖子面板显示
                const createPostPanel = document.querySelector('.create-post-panel');
                if (createPostPanel) createPostPanel.classList.add('visible');
                
                setTimeout(() => {
                    // 统计数据面板显示
                    const statsPanel = document.querySelector('.stats-panel');
                    if (statsPanel) statsPanel.classList.add('visible');
                    
                    setTimeout(() => {
                        // 帖子列表显示
                        const postsContainer = document.querySelector('.posts-container');
                        if (postsContainer) postsContainer.classList.add('visible');
                        
                        // 为每个帖子卡片设置延迟动画
                        const postCards = document.querySelectorAll('.post-card');
                        postCards.forEach((card, index) => {
                            card.style.setProperty('--card-index', index);
                        });
                        
                        // 无内容提示显示
                        const noContent = document.querySelector('.no-content');
                        if (noContent) noContent.classList.add('visible');
                    }, 200);
                }, 200);
            }, 200);
        }, 500);
    }, 300);
    
    // 侧边栏切换
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const contentArea = document.getElementById('content-area');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (sidebar) sidebar.classList.toggle('collapsed');
            contentArea.classList.toggle('expanded');
            
            // 切换图标
            const icon = sidebarToggle.querySelector('i');
            if (icon) {
                if (icon.classList.contains('fa-chevron-left')) {
                    icon.classList.remove('fa-chevron-left');
                    icon.classList.add('fa-chevron-right');
                } else {
                    icon.classList.remove('fa-chevron-right');
                    icon.classList.add('fa-chevron-left');
                }
            }
        });
    }
    
    // 学生名单切换
    const toggleStudentList = document.getElementById('toggle-student-list');
    const studentList = document.getElementById('student-list');
    
    if (toggleStudentList && studentList) {
        toggleStudentList.addEventListener('click', function() {
            studentList.classList.toggle('active');
        });
    }
    
    // 初始化所有可折叠面板
    initCollapsiblePanels();
});

// 可折叠面板初始化
function initCollapsiblePanels() {
    const panels = document.querySelectorAll('.panel-header');
    
    panels.forEach(panel => {
        panel.addEventListener('click', function() {
            // 切换内容区域
            const content = this.nextElementSibling;
            content.classList.toggle('expanded');
            
            // 切换图标
            const icon = this.querySelector('.toggle-icon');
            if (icon) {
                icon.classList.toggle('collapsed');
            }
        });
    });
}

// 切换更多菜单
function toggleMoreMenu(postId) {
    const menu = document.getElementById(`more-menu-${postId}`);
    menu.classList.toggle('active');
    
    // 关闭其他打开的菜单
    document.querySelectorAll('.more-menu.active').forEach(item => {
        if (item.id !== `more-menu-${postId}`) {
            item.classList.remove('active');
        }
    });
    
    // 阻止事件冒泡
    event.stopPropagation();
}

// 点击页面其他地方关闭菜单
document.addEventListener('click', function() {
    document.querySelectorAll('.more-menu.active').forEach(item => {
        item.classList.remove('active');
    });
});

// 展示帖子到中央
function highlightPost(postId) {
    const postCard = document.getElementById(`post-${postId}`);
    
    // 移除其他帖子的高亮
    document.querySelectorAll('.post-card.highlighted').forEach(item => {
        item.classList.remove('highlighted');
    });
    
    // 添加高亮到当前帖子
    postCard.classList.toggle('highlighted');
}

// 切换评论区域显示
function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-${postId}`);
    commentsSection.classList.toggle('active');
}

// 切换点赞状态
function toggleLike(postId) {
    const likeBtn = document.querySelector(`#post-${postId} .like-btn`);
    const likeCount = document.querySelector(`#post-${postId} .like-count`);
    
    // 这里应该发送请求到服务器，这里只是前端模拟
    if (likeBtn.classList.contains('active')) {
        likeBtn.classList.remove('active');
        likeCount.textContent = parseInt(likeCount.textContent) - 1;
    } else {
        likeBtn.classList.add('active');
        likeCount.textContent = parseInt(likeCount.textContent) + 1;
    }
}

// 提交评论
function submitComment(event, postId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('.comment-input');
    const commentContent = input.value.trim();
    
    if (commentContent) {
        // 这里应该发送请求到服务器，这里只是前端模拟
        const commentsList = document.querySelector(`#comments-${postId} .comments-list`);
        const noComments = commentsList.querySelector('.no-comments');
        
        if (noComments) {
            noComments.remove();
        }
        
        const newComment = document.createElement('div');
        newComment.className = 'comment';
        newComment.innerHTML = `
            <span class="comment-author">${document.querySelector('.user-info p:first-child').textContent.split('：')[1].trim()}</span>
            <span class="comment-content">${commentContent}</span>
        `;
        
        commentsList.appendChild(newComment);
        
        // 更新评论计数
        const commentCount = document.querySelector(`#post-${postId} .comment-count`);
        commentCount.textContent = parseInt(commentCount.textContent) + 1;
        
        // 清空输入框
        input.value = '';
    }
}

// 显示图片模态框
function showImageModal(imageUrl) {
    const modal = document.getElementById('image-modal');
    const modalImg = modal.querySelector('img');
    
    modalImg.src = imageUrl;
    modal.classList.add('active');
    
    // 阻止事件冒泡
    event.stopPropagation();
}

// 关闭图片模态框
function closeImageModal() {
    const modal = document.getElementById('image-modal');
    modal.classList.remove('active');
}

// 删除帖子
function deletePost(postId) {
    if (confirm('确定要删除这个帖子吗？')) {
        // 这里应该发送请求到服务器，这里只是前端模拟
        const postCard = document.getElementById(`post-${postId}`);
        postCard.style.opacity = '0.5';
        postCard.style.pointerEvents = 'none';
        
        // 添加删除中的提示
        const deleteMsg = document.createElement('div');
        deleteMsg.style.position = 'absolute';
        deleteMsg.style.top = '50%';
        deleteMsg.style.left = '50%';
        deleteMsg.style.transform = 'translate(-50%, -50%)';
        deleteMsg.style.background = 'rgba(0,0,0,0.7)';
        deleteMsg.style.color = 'white';
        deleteMsg.style.padding = '10px 15px';
        deleteMsg.style.borderRadius = '5px';
        deleteMsg.style.zIndex = '10';
        deleteMsg.textContent = '删除中...';
        
        postCard.appendChild(deleteMsg);
        
        // 模拟删除成功后移除帖子
        setTimeout(() => {
            postCard.remove();
            
            // 如果没有帖子了，显示暂无帖子的提示
            const postsContainer = document.getElementById('posts-container');
            if (postsContainer.children.length === 0) {
                const noContent = document.createElement('div');
                noContent.className = 'no-content visible';
                noContent.innerHTML = `
                    <i class="fas fa-inbox" style="font-size: 2rem; color: var(--primary-light); display: block; margin-bottom: 10px;"></i>
                    暂无帖子，快来发布第一个帖子吧！
                `;
                postsContainer.appendChild(noContent);
            }
        }, 1000);
    }
}

// 编辑帖子
function editPost(postId) {
    const postCard = document.getElementById(`post-${postId}`);
    const title = postCard.querySelector('.post-title').textContent;
    const content = postCard.querySelector('.post-content').textContent;
    
    // 填充编辑表单
    document.getElementById('edit-post-id').value = postId;
    document.getElementById('edit-post-title').value = title;
    document.getElementById('edit-post-content').value = content;
    
    // 显示编辑区域
    const editArea = document.getElementById('edit-post-area');
    editArea.style.display = 'block';
    
    // 滚动到编辑区域
    editArea.scrollIntoView({ behavior: 'smooth' });
}

// 取消编辑
function cancelEdit() {
    document.getElementById('edit-post-area').style.display = 'none';
}

// 提交编辑表单
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('edit-post-form');
    if (editForm) {
        editForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const postId = document.getElementById('edit-post-id').value;
            const title = document.getElementById('edit-post-title').value;
            const content = document.getElementById('edit-post-content').value;
            
            // 这里应该发送请求到服务器，这里只是前端模拟
            const postCard = document.getElementById(`post-${postId}`);
            postCard.querySelector('.post-title').textContent = title;
            postCard.querySelector('.post-content').textContent = content;
            
            // 隐藏编辑区域
            document.getElementById('edit-post-area').style.display = 'none';
            
            // 显示成功提示
            alert('帖子更新成功！');
        });
    }
    
    // 提交新帖子表单
    const createForm = document.getElementById('create-post-form');
    if (createForm) {
        createForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const title = document.getElementById('post-title').value;
            const content = document.getElementById('post-content').value;
            const imageInput = document.getElementById('post-image');
            
            // 这里应该发送请求到服务器，这里只是前端模拟
            // 创建新帖子元素
            const newPostId = Date.now(); // 使用时间戳作为临时ID
            
            const postsContainer = document.getElementById('posts-container');
            const noContent = postsContainer.querySelector('.no-content');
            
            if (noContent) {
                noContent.remove();
            }
            
            const newPost = document.createElement('div');
            newPost.className = 'post-card';
            newPost.id = `post-${newPostId}`;
            newPost.dataset.postId = newPostId;
            newPost.style.setProperty('--card-index', '0');
            
            let imageHtml = '';
            if (imageInput.files.length > 0) {
                const file = imageInput.files[0];
                const imageUrl = URL.createObjectURL(file);
                
                imageHtml = `
                    <img src="${imageUrl}" alt="${title}" class="post-image" onclick="showImageModal('${imageUrl}')">
                    <div style="margin-bottom:10px;">
                        <a href="${imageUrl}" target="_blank" class="btn" style="padding:6px 12px; font-size:0.85rem;">
                            <i class="fas fa-download" style="margin-right: 5px;"></i> 下载附件
                        </a>
                    </div>
                `;
            }
            
            const userRole = document.querySelector('.user-info p:nth-child(2)').textContent.split('：')[1].trim();
            let actionsHtml = '';
            
            if (userRole === "teacher") {
                actionsHtml = `
                    <div class="post-actions">
                        <button class="more-btn" onclick="toggleMoreMenu('${newPostId}')">⋮</button>
                        <div class="more-menu" id="more-menu-${newPostId}">
                            <button onclick="highlightPost('${newPostId}')">
                                <i class="fas fa-star" style="margin-right: 5px;"></i> 展示到中央
                            </button>
                            <button onclick="deletePost('${newPostId}')">
                                <i class="fas fa-trash" style="margin-right: 5px;"></i> 删除帖子
                            </button>
                            <button onclick="editPost('${newPostId}')">
                                <i class="fas fa-edit" style="margin-right: 5px;"></i> 编辑帖子
                            </button>
                        </div>
                    </div>
                `;
            } else {
                actionsHtml = `
                    <div class="post-actions">
                        <button class="more-btn" onclick="toggleMoreMenu('${newPostId}')">⋮</button>
                        <div class="more-menu" id="more-menu-${newPostId}">
                            <button onclick="deletePost('${newPostId}')">
                                <i class="fas fa-trash" style="margin-right: 5px;"></i> 删除帖子
                            </button>
                            <button onclick="editPost('${newPostId}')">
                                <i class="fas fa-edit" style="margin-right: 5px;"></i> 编辑帖子
                            </button>
                        </div>
                    </div>
                `;
            }
            
            const now = new Date();
            const formattedDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            const userName = document.querySelector('.user-info p:first-child').textContent.split('：')[1].trim();
            
            newPost.innerHTML = `
                ${actionsHtml}
                <h3 class="post-title">${title}</h3>
                ${imageHtml}
                <p class="post-content">${content}</p>
                <div class="post-meta">
                    <span><i class="fas fa-user" style="margin-right: 5px; opacity: 0.7;"></i>${userName}</span>
                    <span><i class="fas fa-clock" style="margin-right: 5px; opacity: 0.7;"></i>${formattedDate}</span>
                </div>
                <div class="post-interactions">
                    <button class="post-interaction-btn like-btn" onclick="toggleLike('${newPostId}')">
                        <i class="fas fa-thumbs-up"></i>
                        <span class="like-count">0</span>
                    </button>
                    <button class="post-interaction-btn comment-btn" onclick="toggleComments('${newPostId}')">
                        <i class="fas fa-comment"></i>
                        <span class="comment-count">0</span>
                    </button>
                </div>
                <div class="comments-section" id="comments-${newPostId}">
                    <div class="comments-list">
                        <div class="no-comments" style="color: var(--text-light); font-style: italic; padding: 10px 0;">暂无评论</div>
                    </div>
                    <form class="comment-form" onsubmit="submitComment(event, '${newPostId}')">
                        <input type="text" class="comment-input" placeholder="添加评论..." required>
                        <button type="submit" class="comment-submit">发送</button>
                    </form>
                </div>
            `;
            
            // 将新帖子添加到容器的最前面
            postsContainer.insertBefore(newPost, postsContainer.firstChild);
            
            // 重置表单
            document.getElementById('create-post-form').reset();
            
            // 显示成功提示
            alert('帖子发布成功！');
        });
    }
});
