// 初始化Socket.IO连接
const socket = io();

// 获取DOM元素
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');
const agentList = document.querySelector('.agent-list');

// 当前对话轮次
let currentRound = 0;

// 自动对话状态
let isAutoChatting = false;
let autoChatInterval = null;

// 初始化智能体列表
function initializeAgents() {
    const roles = [
        "暴躁贴吧老哥",
        "阴阳怪气的乐子人",
        "暴躁老哥支持者",
        "纯路人",
        "理性分析者",
        "幽默段子手",
        "知识分享者",
        "情感咨询师",
        "技术专家",
        "生活达人"
    ];

    roles.forEach(role => {
        const agentTag = document.createElement('div');
        agentTag.className = 'agent-tag';
        agentTag.textContent = role;
        agentList.appendChild(agentTag);
    });
}

// 添加消息到聊天界面
function addMessage(content, sender, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'agent'}`;
    
    const header = document.createElement('div');
    header.className = 'message-header';
    
    // 如果是用户消息，显示"你"
    if (isUser) {
        header.textContent = sender;
    } else {
        // 如果是agent消息，显示agent ID和名称
        const agentId = sender.split('(')[0].trim();
        const agentName = sender.split('(')[1].replace(')', '').trim();
        header.innerHTML = `<span class="agent-id">${agentId}</span> <span class="agent-name">${agentName}</span>`;
        
        // 添加轮次信息
        const roundInfo = document.createElement('div');
        roundInfo.className = 'round-info';
        roundInfo.textContent = `第 ${currentRound} 轮`;
        messageDiv.appendChild(roundInfo);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(header);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 发送消息
function sendMessage(message) {
    if (message) {
        // 添加用户消息到界面
        addMessage(message, '你', true);
        
        // 发送消息到服务器
        socket.emit('send_message', {
            message: message,
            round: currentRound
        });
        
        // 清空输入框
        messageInput.value = '';
        
        // 增加轮次
        currentRound++;
        
        // 开始自动对话
        startAutoChat();
    }
}

// 处理接收到的消息
socket.on('agent_message', (data) => {
    console.log('Received message data:', data);
    const agentName = data.name || '未知智能体';
    const agentId = data.sender || 'unknown';
    const sender = `${agentId} (${agentName})`;
    addMessage(data.content, sender);
    
    // 如果是网警的消息，直接进入下一轮
    if (data.sender === 'agent2') {
        if (currentRound < 20) {
            setTimeout(() => {
                startNextRound();
            }, 2000); // 等待2秒后进入下一轮
        }
    }
});

// 处理违规消息
socket.on('violation_alert', (data) => {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'message violation';
    alertDiv.textContent = `⚠️ ${data.message}`;
    chatMessages.appendChild(alertDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

// 生成随机消息
function generateRandomMessage() {
    // 发送请求到后端获取 AI 生成的回复
    fetch('/generate_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            conversation_history: conversation_state.conversation_history,
            current_round: currentRound
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // 添加用户消息到界面
            addMessage(data.message, '你', true);
            
            // 发送消息到服务器
            socket.emit('send_message', {
                message: data.message,
                round: currentRound
            });
            
            // 增加轮次
            currentRound++;
        } else {
            console.error('Failed to generate message');
            stopAutoChat();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        stopAutoChat();
    });
}

// 开始自动对话
function startAutoChat() {
    if (!isAutoChatting) {
        isAutoChatting = true;
        sendButton.textContent = '停止对话';
        sendButton.style.backgroundColor = '#dc3545'; // 红色
        messageInput.disabled = true;
        messageInput.placeholder = '智能体自主对话进行中...';
        
        // 开始第一轮对话
        startNextRound();
    }
}

// 停止自动对话
function stopAutoChat() {
    if (isAutoChatting) {
        isAutoChatting = false;
        clearInterval(autoChatInterval);
        sendButton.textContent = '发送';
        sendButton.style.backgroundColor = '#4a90e4'; // 恢复蓝色
        messageInput.disabled = false;
        messageInput.placeholder = '输入第一条消息开始自动对话...';
    }
}

// 修改发送按钮点击事件
sendButton.addEventListener('click', () => {
    if (isAutoChatting) {
        stopAutoChat();
    } else {
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
            startAutoChat(); // 发送第一条消息后开始自动对话
        }
    }
});

// 修改输入框回车事件
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !isAutoChatting) {
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
            startAutoChat(); // 发送第一条消息后开始自动对话
        }
    }
});

// 监听对话结束事件
socket.on('conversation_end', (data) => {
    stopAutoChat();
    addMessage(data.message, '系统', false);
});

// 处理轮次更新
socket.on('round_update', (data) => {
    // 不在这里更新轮次，只在系统生成用户消息时更新
    console.log('Received round update:', data);
});

// 开始下一轮对话
function startNextRound() {
    // 发送空消息触发下一轮对话
    socket.emit('send_message', {
        message: '',
        round: currentRound
    });
    currentRound++;
}

// 初始化
initializeAgents(); 