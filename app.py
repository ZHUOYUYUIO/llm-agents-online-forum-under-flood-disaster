from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
import traceback
import uuid
import datetime
import re
import random
import time
import numpy as np
from openai import OpenAI
from flask_socketio import SocketIO, emit
import logging
import threading
from datetime import datetime, timedelta
from persona_generator import generate_all_personas


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 打印调试信息
print("开始初始化应用...")

# 尝试加载环境变量
load_dotenv()
print("环境变量加载完成")

# 初始化OpenAI客户端
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    print("警告: 未设置 OPENAI_API_KEY 环境变量")
    API_KEY = input("请输入您的 DeepSeek API Key: ").strip()
os.environ['OPENAI_API_KEY'] = API_KEY
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com/v1")

# 初始化应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'multi_agent_chat_system'
print("Flask应用初始化完成")

# 初始化Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', 
                   ping_timeout=60, ping_interval=25, 
                   max_http_buffer_size=1e8)
print("Socket.IO初始化完成")

# 定义颜色映射
COLORS = {
    "agent1": "#FF0000",   # 红色
    "agent2": "#00FF00",   # 绿色
    "agent3": "#FFFF00",   # 黄色
    "agent4": "#0000FF",   # 蓝色
    "agent5": "#FF00FF",   # 紫色
    "agent6": "#00FFFF",   # 青色
    "agent7": "#FF3333",   # 亮红
    "agent8": "#33FF33",   # 亮绿
    "agent9": "#FFFF33",   # 亮黄
    "agent10": "#3333FF",  # 亮蓝
    "agent11": "#FF33FF",  # 亮紫
    "agent12": "#33FFFF",  # 亮青
    "agent13": "#FF6666",  # 红底
    "agent14": "#66FF66",  # 绿底
    "agent15": "#FFFF66",  # 黄底
    "agent16": "#6666FF",  # 蓝底
    "agent17": "#FF66FF",  # 紫底
    "agent18": "#66FFFF",  # 青底
    "agent19": "#FF9999",  # 亮红加粗
    "agent20": "#99FF99",  # 亮绿加粗
    "agent21": "#FFFF99",  # 亮黄加粗
    "agent22": "#9999FF",  # 亮蓝加粗
    "agent23": "#FF99FF",  # 亮紫加粗
    "agent24": "#99FFFF",  # 亮青加粗
    "agent25": "#FFCCCC",  # 红下划线
    "agent26": "#CCFFCC",  # 绿下划线
    "agent27": "#FFFFCC",  # 黄下划线
    "agent28": "#CCCCFF",  # 蓝下划线
    "agent29": "#FFCCFF",  # 紫下划线
    "agent30": "#CCFFFF",  # 青下划线
    "agent31": "#FFE6E6",  # 红反显
    "agent32": "#E6FFE6",  # 绿反显
    "agent33": "#FFFFE6",  # 黄反显
    "agent34": "#E6E6FF",  # 蓝反显
    "agent35": "#FFE6FF",  # 紫反显
    "agent36": "#E6FFFF",  # 青反显
    "agent37": "#FFB3B3",  # 红闪烁
    "agent38": "#B3FFB3",  # 绿闪烁
    "agent39": "#FFFFB3",  # 黄闪烁
    "agent40": "#B3B3FF",  # 蓝闪烁
    "agent41": "#FFB3FF",  # 紫闪烁
    "agent42": "#B3FFFF",  # 青闪烁
    "agent43": "#FF8080",  # 红斜体
    "agent44": "#80FF80",  # 绿斜体
    "agent45": "#FFFF80",  # 黄斜体
    "agent46": "#8080FF",  # 蓝斜体
    "agent47": "#FF80FF",  # 紫斜体
    "agent48": "#80FFFF",  # 青斜体
    "agent49": "#FF4D4D",  # 红斜体
    "agent50": "#4DFF4D"   # 绿斜体
}

# 定义角色颜色映射
color_mapping = {
    "程序员": "#FF0000",
    "教师": "#00FF00",
    "医生": "#FFFF00",
    "律师": "#0000FF",
    "设计师": "#FF00FF",
    "作家": "#00FFFF",
    "记者": "#FF3333",
    "工程师": "#33FF33",
    "销售": "#FFFF33",
    "厨师": "#3333FF",
    "摄影师": "#FF3333",
    "音乐人": "#33FF33",
    "自由职业者": "#FFFF33",
    "学生": "#3333FF",
    "公务员": "#FF3333",
    "商人": "#33FF33",
    "艺术家": "#FFFF33",
    "心理咨询师": "#3333FF",
    "翻译": "#FF3333",
    "导游": "#33FF33",
    "健身教练": "#FFFF33",
    "主播": "#3333FF",
    "编辑": "#FF3333",
    "研究员": "#33FF33",
    "建筑师": "#FFFF33",
    "网警": "#FF0000"  # 网警使用红色
}

# 定义违禁词列表及变体映射
BANNED_WORDS = {
    "典": ["典", "点", "電", "dian"],
    "急": ["急", "及", "级", "ji"],
    "孝": ["孝", "笑", "效", "xiao"],
    "屁": ["屁", "p", "批", "pi"]
}

class EnhancedMemoryStream:
    def __init__(self):
        self.seq_nodes = []
        self.reflections = []
        self.importance_threshold = 0.5

    def _add_node(self, time_step, node_type, content, importance):
        self.seq_nodes.append({
            'time_step': time_step,
            'type': node_type,
            'content': content,
            'importance': importance
        })

    def retrieve_context(self, query, k):
        # 简单的基于重要性的检索
        sorted_nodes = sorted(self.seq_nodes, key=lambda x: x['importance'], reverse=True)
        return [node['content'] for node in sorted_nodes[:k]]

    def generate_reflections(self, k):
        # 基于最近k个节点生成反思
        recent_nodes = self.seq_nodes[-k:]
        if len(recent_nodes) >= 3:
            reflection = f"基于最近{k}个对话节点，系统观察到："
            self.reflections.append(reflection)

def contains_violation(text):
    """改进的违规词检测"""
    text = text.lower()
    for base_word, variants in BANNED_WORDS.items():
        if any(v in text for v in variants):
            return (True, base_word)
    return (False, None)

# 添加对话状态管理
class ConversationState:
    def __init__(self):
        self.is_active = False
        self.current_round = 0
        self.max_rounds = 20
        self.last_message_time = None
        self.conversation_history = []

    def start_conversation(self):
        self.is_active = True
        self.current_round = 0
        self.conversation_history = []
        self.last_message_time = datetime.now()

    def end_conversation(self):
        self.is_active = False
        self.current_round = 0
        self.conversation_history = []
        self.last_message_time = None

    def add_message(self, message):
        self.conversation_history.append({
            'content': message,
            'time': datetime.now(),
            'round': self.current_round
        })
        self.last_message_time = datetime.now()

# 初始化对话状态
conversation_state = ConversationState()

# 添加禁言列表
banned_agents = set()  # 存储被禁言的agent ID

def is_agent_banned(agent_id):
    """检查agent是否被禁言"""
    return agent_id in banned_agents

def ban_agent(agent_id, reason):
    """禁言agent并记录原因"""
    banned_agents.add(agent_id)
    # 在agent的历史记录中添加禁言记录
    if agent_id in agents:
        agents[agent_id]['history'].append({
            'role': 'system',
            'content': f"【禁言通知】由于{reason}，你已被网警禁言。",
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

def should_agent_reply(agent_id, agent_info, conversation_history, memory, current_round):
    """改进的基于轮次的智能体回复决策"""
    try:
        # 网警特殊处理 - 每轮都参与
        if agent_id == "agent2":
            return True
        
        # 动态调整基础回复概率（每轮降低3%，而不是5%）
        base_prob = max(0.3, 0.7 - current_round * 0.03)
        
        # 话题相关性检查
        topic_words = agent_info['topic'].lower().split()
        msg_text = " ".join([msg["content"] for msg in conversation_history[-5:]])  # 使用最近3条消息
        topic_relevance = any(word in msg_text.lower() for word in topic_words)
        
        # 上下文相关性检查
        context = memory_stream.retrieve_context(msg_text, min(5, len(memory_stream.seq_nodes)))  # 限制检索数量
        context_relevance = any(agent_id in msg for msg in context)
        
        # 随机性调整
        random_factor = random.uniform(0.9, 1.1)  # 减小随机性范围
        
        # 综合决策
        if topic_relevance or context_relevance:
            return random.random() < min(0.95, (base_prob + 0.2) * random_factor)
        return random.random() < base_prob * random_factor
        
    except Exception as e:
        logger.error(f"Error in should_agent_reply: {str(e)}")
        return False

def chat_with_agent(prompt, conversation_history, role_description, agent_id, current_round):
    """改进的带轮次感知的聊天函数"""
    try:
        # 如果agent被禁言，直接返回禁言提示
        if is_agent_banned(agent_id):
            return f"【禁言中】该账号已被网警禁言，无法发言。"
            
        # 添加轮次信息到系统提示
        system_msg = f"{role_description}\n【当前对话轮次】{current_round}\n请用20字内口语化回复，禁用任何标记符号。"
        
        # 网警专用提示
        if agent_id == "agent2":
            violated, word = contains_violation(prompt)
            if violated:
                # 找出违规的agent
                for msg in conversation_history:
                    if word in msg["content"].lower():
                        violating_agent = msg["sender"]
                        # 禁言违规agent
                        ban_agent(violating_agent, f"使用违禁词'{word}'的变体")
                        system_msg = f"你发现{violating_agent}使用了违禁词'{word}'的变体，已将其禁言。"
        
        # 构建对话历史
        messages = [{"role": "system", "content": system_msg}]
        for msg in conversation_history[-10:]:  # 只使用最近10条消息
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})
        
        print(f"Agent {agent_id} 正在处理消息...")
        print(f"系统提示: {system_msg}")
        print(f"用户消息: {prompt}")
        
        # 调用API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=50,
            temperature=0.7
        )
        
        if response and response.choices:
            reply = response.choices[0].message.content
            print(f"Agent {agent_id} 回复: {reply}")
            return reply
        else:
            print(f"Agent {agent_id} 未获得有效回复")
            return None
            
    except Exception as e:
        logger.error(f"Agent {agent_id} chat error: {str(e)}")
        print(f"Agent {agent_id} 发生错误: {str(e)}")
        return None

def handle_reflection(current_round):
    """基于轮次的记忆反思"""
    if current_round % 5 == 0:  # 改为每5轮进行反思，避免与7轮冲突
        memory_stream.generate_reflections(len(memory_stream.seq_nodes))

def evaluate_agent_response(agent_id, agent_info, recent_history, current_round):
    """评估智能体是否愿意回复"""
    # 如果agent被禁言，直接返回0分
    if is_agent_banned(agent_id):
        return 0.0
        
    try:
        # 构建评估提示
        system_prompt = f"""你是一个{agent_info['name']}，主要{agent_info['topic']}。
请评估你是否愿意参与当前对话，并给出一个0-1的评分。
评分标准：
1. 话题相关性
2. 个人兴趣
3. 回复必要性
4. 对话连贯性

请只返回一个0-1的浮点数，不要包含其他文字。"""
        
        # 构建对话历史
        messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 调用 DeepSeek API 进行评估
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=10,
            temperature=0.3
        )
        
        if response and response.choices:
            try:
                score = float(response.choices[0].message.content.strip())
                return min(max(score, 0), 1)  # 确保分数在0-1之间
            except ValueError:
                return 0.5  # 如果解析失败，返回默认值
        return 0.5
        
    except Exception as e:
        logger.error(f"Error in evaluate_agent_response: {str(e)}")
        return 0.5

def select_responding_agents(current_round, max_responders=4):
    """选择回复的智能体"""
    try:
        # 获取所有智能体的历史记录
        all_history = []
        for agent in agents.values():
            if agent['history']:
                all_history.extend(agent['history'][-3:])
        all_history.sort(key=lambda x: x.get('time', ''))
        
        # 随机抽取20个智能体进行评估（如果总数不足20个，则评估所有）
        available_agents = [agent_id for agent_id in agents.keys() 
                          if agent_id != "agent2" and not is_agent_banned(agent_id)]
        sample_size = min(20, len(available_agents))
        sampled_agents = random.sample(available_agents, sample_size)
        
        # 评估抽中的智能体的回复意愿
        agent_scores = {}
        for agent_id in sampled_agents:
            agent_info = agents[agent_id]
            score = evaluate_agent_response(agent_id, agent_info, all_history, current_round)
            agent_scores[agent_id] = score
            print(f"{agent_id} ({agent_info['name']}) 回复意愿评分: {score}")
        
        # 按评分排序并选择最高分的智能体
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        selected_agents = [agent_id for agent_id, score in sorted_agents[:max_responders]]
        
        # 确保网警在最后
        selected_agents.append("agent2")
        
        return selected_agents
        
    except Exception as e:
        logger.error(f"Error in select_responding_agents: {str(e)}")
        return []

@socketio.on('send_message')
def handle_message(data):
    try:
        message = data.get('message', '')
        current_round = data.get('round', 0)
        
        # 更新对话状态
        if not conversation_state.is_active:
            conversation_state.start_conversation()
        conversation_state.current_round = current_round
        if message:  # 只在有消息时添加到历史
            conversation_state.add_message(message)
        
        print(f"\n开始处理第{current_round}轮对话")
        if message:
            print(f"收到消息: {message}")
        
        # 检查是否达到最大轮次
        if current_round >= conversation_state.max_rounds:
            print("达到最大对话轮次，结束对话")
            conversation_state.end_conversation()
            emit('conversation_end', {'message': '对话已达到最大轮次'})
            return
        
        # 固定每轮回复人数为4人（不包括网警）
        max_responders = 10
        print(f"本轮最大回复人数: {max_responders}")
        
        # 获取响应智能体
        responding_agents = select_responding_agents(current_round, max_responders)
        
        print(f"准备回复的智能体: {responding_agents}")
        
        # 添加轮次记忆
        memory_stream._add_node(
            time_step=len(memory_stream.seq_nodes),
            node_type="system",
            content=f"第{current_round}轮对话开始",
            importance=6
        )
        
        # 处理回复
        for agent_id in responding_agents:
            agent = agents[agent_id]
            print(f"\n处理 {agent_id} ({agent['name']}) 的回复...")
            
            # 获取最近的对话历史（限制数量）
            recent_history = []
            for other_agent in agents.values():
                if other_agent['history']:
                    recent_history.extend(other_agent['history'][-20:])  # 只获取最近2条消息
            recent_history.sort(key=lambda x: x.get('time', ''))
            
            response = chat_with_agent(message, recent_history, agent['desc'], agent_id, current_round)
            
            if response:
                print(f"{agent_id} 回复成功: {response}")
                # 发送消息到前端
                emit('agent_message', {
                    'content': response,
                    'sender': agent_id,
                    'name': agent['name'],
                    'color': color_mapping.get(agent['name'], '#333333')
                })
                
                # 更新历史记录
                agent['history'].append({
                    'role': 'assistant',
                    'content': response,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # 添加到记忆流
                memory_stream._add_node(
                    time_step=len(memory_stream.seq_nodes),
                    node_type="observation",
                    content=f"[R{current_round}] {agent_id}: {response}",
                    importance=8
                )
            else:
                print(f"{agent_id} 未获得回复")
        
        # 进行周期性的记忆反思
        handle_reflection(current_round)
        
        print(f"第{current_round}轮对话处理完成\n")
        
    except Exception as e:
        logger.error(f"Message handling error: {str(e)}")
        print(f"处理消息时发生错误: {str(e)}")
        emit('error', {'message': '处理消息时发生错误'})
        conversation_state.end_conversation()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_message', methods=['POST'])
def generate_message():
    try:
        data = request.get_json()
        conversation_history = data.get('conversation_history', [])
        current_round = data.get('current_round', 0)
        
        # 构建系统提示
        system_prompt = """你是一个多智能体对话系统中的用户角色。请根据对话历史生成一个自然、有趣的回复。
回复应该：
1. 保持对话的连贯性
2. 展现真实的对话风格
3. 避免重复之前的内容
4. 长度在20字以内
5. 使用口语化表达
6. 根据当前对话轮次调整回复风格（前期活跃，后期逐渐深入）"""
        
        # 构建对话历史
        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history[-5:]:  # 只使用最近5条消息
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=50,
            temperature=0.8
        )
        
        if response and response.choices:
            generated_message = response.choices[0].message.content
            return jsonify({"message": generated_message})
        else:
            return jsonify({"error": "Failed to generate message"}), 500
            
    except Exception as e:
        logger.error(f"Error in generate_message: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 初始化记忆流
memory_stream = EnhancedMemoryStream()

# 初始化智能体
agents = {}

# 初始化网警
agents["agent2"] = {
    'name': "网警",
    'desc': "你是一个网警，负责监控对话中的违规内容。当发现违规时，直接指出违规的agent和关键词。",
    'topic': "监控违规内容",
    'history': [],
    'color': color_mapping["网警"]
}

# 使用persona_generator生成其他智能体的人设信息
personas = generate_all_personas(100)  # 生成100个agent的人设

# 初始化其他智能体
for agent_id, persona in personas.items():
    # 构建agent的描述，包含人设信息
    desc = f"""你是一个{persona['occupation']}，{persona['gender']}，{persona['age']}岁，来自{persona['location']}。
你的性格特点是：{', '.join(persona['personality'])}。
你的兴趣爱好是：{', '.join(persona['interests'])}。
你是一个{persona['online_chat_traits']['活跃度']}，喜欢讨论{', '.join(persona['online_chat_traits']['话题偏好'])}。
你的回复风格是{persona['online_chat_traits']['回复风格']}。
{persona['background']}
请保持这些特点进行对话。"""
    
    agents[agent_id] = {
        'name': persona['occupation'],  # 使用职业作为名称
        'desc': desc,
        'topic': persona['online_chat_traits']['话题偏好'][0],  # 使用第一个话题偏好作为主题
        'history': [],
        'color': color_mapping.get(persona['occupation'], '#333333'),
        'persona': persona  # 保存完整的人设信息
    }

print("智能体初始化完成")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8081, debug=True)