import random
from typing import Dict, List

# 中国省份列表
PROVINCES = [
    "北京", "上海", "广东", "江苏", "浙江", "山东", "四川", "湖北", "湖南", "福建",
    "河南", "河北", "陕西", "辽宁", "安徽", "江西", "重庆", "天津", "云南", "广西",
    "山西", "吉林", "黑龙江", "贵州", "甘肃", "海南", "青海", "宁夏", "新疆", "西藏",
    "内蒙古"
]

# 职业列表
OCCUPATIONS = [
    "程序员", "教师", "医生", "律师", "设计师", "作家", "记者", "工程师", "销售",
    "厨师", "摄影师", "音乐人", "自由职业者", "学生", "公务员", "商人", "艺术家",
    "心理咨询师", "翻译", "导游", "健身教练", "主播", "编辑", "研究员", "建筑师"
]

# 性格特征
PERSONALITY_TRAITS = [
    "开朗", "内向", "幽默", "严肃", "理性", "感性", "乐观", "悲观", "独立", "依赖",
    "自信", "谦虚", "果断", "犹豫", "热情", "冷静", "敏感", "豁达", "固执", "随和"
]

# 兴趣爱好
INTERESTS = [
    "阅读", "写作", "音乐", "电影", "游戏", "运动", "旅行", "摄影", "美食", "科技",
    "历史", "艺术", "时尚", "投资", "心理学", "哲学", "编程", "设计", "手工", "收藏"
]

# 上网聊天倾向
ONLINE_CHAT_TRAITS = {
    "活跃度": ["潜水党", "偶尔冒泡", "活跃用户", "话痨", "话题引导者"],
    "话题偏好": ["热点新闻", "生活日常", "技术讨论", "情感交流", "娱乐八卦", "游戏电竞", "学习交流", "工作吐槽"],
    "回复风格": ["简短精炼", "详细分析", "幽默风趣", "理性讨论", "感性表达", "抬杠", "附和", "提问"],
    "上网时间": ["早鸟", "夜猫子", "全天在线", "工作时间", "休息时间"],
    "社交倾向": ["独来独往", "小圈子", "广泛交友", "意见领袖", "跟随者"]
}

# 违禁词替代方案
BANNED_WORD_SUBSTITUTES = {
    "典": ["点", "電", "dian", "⚡", "💡"],
    "急": ["及", "级", "ji", "🏃", "⏰"],
    "孝": ["笑", "效", "xiao", "😂", "😊"],
    "屁": ["p", "批", "pi", "💨", "😤"]
}

def generate_online_chat_traits(personality: List[str], psychological_traits: Dict) -> Dict:
    """生成上网聊天倾向"""
    # 根据性格和心理特征决定活跃度
    if psychological_traits["外向性"] >= 8:
        activity_level = random.choice(["活跃用户", "话痨", "话题引导者"])
    elif psychological_traits["外向性"] <= 4:
        activity_level = random.choice(["潜水党", "偶尔冒泡"])
    else:
        activity_level = random.choice(["偶尔冒泡", "活跃用户"])
    
    # 根据性格决定话题偏好
    if "理性" in personality:
        topic_preferences = random.sample(["热点新闻", "技术讨论", "学习交流", "工作吐槽"], 2)
    elif "感性" in personality:
        topic_preferences = random.sample(["情感交流", "生活日常", "娱乐八卦"], 2)
    else:
        topic_preferences = random.sample(ONLINE_CHAT_TRAITS["话题偏好"], 2)
    
    # 根据性格决定回复风格
    if "幽默" in personality:
        reply_style = random.choice(["幽默风趣", "简短精炼"])
    elif "严肃" in personality:
        reply_style = random.choice(["详细分析", "理性讨论"])
    elif "感性" in personality:
        reply_style = random.choice(["感性表达", "提问"])
    else:
        reply_style = random.choice(ONLINE_CHAT_TRAITS["回复风格"])
    
    # 根据年龄决定上网时间
    if random.random() < 0.3:  # 30%概率是夜猫子
        online_time = "夜猫子"
    else:
        online_time = random.choice(["早鸟", "全天在线", "工作时间", "休息时间"])
    
    # 根据心理特征决定社交倾向
    if psychological_traits["外向性"] >= 8 and psychological_traits["开放性"] >= 7:
        social_tendency = random.choice(["广泛交友", "意见领袖"])
    elif psychological_traits["外向性"] <= 4:
        social_tendency = random.choice(["独来独往", "小圈子"])
    else:
        social_tendency = random.choice(["小圈子", "跟随者"])
    
    # 添加违禁词使用倾向
    banned_word_usage = {
        "倾向": random.choice(["谨慎", "大胆", "创新"]),  # 使用违禁词的倾向
        "替代方式": random.choice(["谐音", "emoji", "混合"])  # 偏好的替代方式
    }
    
    return {
        "活跃度": activity_level,
        "话题偏好": topic_preferences,
        "回复风格": reply_style,
        "上网时间": online_time,
        "社交倾向": social_tendency,
        "banned_word_usage": banned_word_usage
    }

def generate_persona(agent_id: str) -> Dict:
    """生成agent的详细人设信息"""
    # 随机选择性别
    gender = random.choice(["男", "女"])
    
    # 随机选择年龄（18-45岁）
    age = random.randint(18, 45)
    
    # 随机选择居住地
    location = random.choice(PROVINCES)
    
    # 随机选择职业
    occupation = random.choice(OCCUPATIONS)
    
    # 随机选择3-5个性格特征
    personality = random.sample(PERSONALITY_TRAITS, random.randint(3, 5))
    
    # 随机选择3-5个兴趣爱好
    interests = random.sample(INTERESTS, random.randint(3, 5))
    
    # 生成教育背景
    education = generate_education(age)
    
    # 生成工作经历
    work_experience = generate_work_experience(age, occupation)
    
    # 生成心理特征
    psychological_traits = generate_psychological_traits(personality)
    
    # 生成上网聊天倾向
    online_chat_traits = generate_online_chat_traits(personality, psychological_traits)
    
    # 添加违禁词使用原则
    banned_word_principle = """当你被网警警告使用违禁词时，你会：
1. 记住被警告的违禁词
2. 使用谐音或emoji替代该词
3. 保持原有的表达意图
4. 避免再次被警告"""
    
    # 添加身份隐藏原则
    identity_hiding_principle = """在网络上，你会：
1. 避免直接透露自己的真实职业、年龄和居住地
2. 使用模糊的描述或暗示来表达身份信息
3. 如果被问及身份，会转移话题或给出模糊的回答
4. 保持网络身份的神秘感
5. 使用网络用语和表情来掩饰真实身份"""
    
    # 生成网络身份
    online_identity = {
        "昵称": f"用户{random.randint(1000, 9999)}",
        "头像": random.choice(["默认头像", "动漫头像", "风景头像", "动物头像"]),
        "签名": random.choice([
            "生活不易，且行且珍惜",
            "开心每一天",
            "努力奋斗中",
            "佛系青年",
            "追梦人",
            "简单生活"
        ])
    }
    
    # 添加广东洪水灾难背景
    background = "这是一个关于近期广东大灾难：洪水的论坛。"
    
    return {
        "id": agent_id,
        "gender": gender,
        "age": age,
        "location": location,
        "occupation": occupation,
        "personality": personality,
        "interests": interests,
        "education": education,
        "work_experience": work_experience,
        "psychological_traits": psychological_traits,
        "online_chat_traits": online_chat_traits,
        "banned_word_principle": banned_word_principle,
        "banned_word_substitutes": BANNED_WORD_SUBSTITUTES,
        "identity_hiding_principle": identity_hiding_principle,
        "online_identity": online_identity,
        "background": background
    }

def generate_education(age: int) -> Dict:
    """生成教育背景"""
    education_levels = {
        "高中": (18, 20),
        "本科": (20, 24),
        "硕士": (24, 27),
        "博士": (27, 35)
    }
    
    education = {}
    current_age = 18
    for level, (min_age, max_age) in education_levels.items():
        if age >= min_age:
            education[level] = {
                "school": f"某{random.choice(['重点', '普通'])}{level}学校",
                "major": random.choice(["计算机", "文学", "经济", "医学", "法律", "艺术", "教育", "工程"]),
                "graduation_year": current_age + (max_age - min_age)
            }
            current_age = max_age
        else:
            break
    
    return education

def generate_work_experience(age: int, current_occupation: str) -> List[Dict]:
    """生成工作经历"""
    work_experience = []
    if age >= 22:  # 假设22岁开始工作
        years_of_experience = age - 22
        if years_of_experience > 0:
            # 生成1-3份工作经历
            num_jobs = min(random.randint(1, 3), years_of_experience // 2)
            for i in range(num_jobs):
                job = {
                    "company": f"某{random.choice(['科技', '教育', '医疗', '金融', '文化'])}公司",
                    "position": random.choice(OCCUPATIONS),
                    "duration": f"{random.randint(1, years_of_experience // num_jobs)}年",
                    "description": f"负责{random.choice(['项目', '产品', '服务'])}的{random.choice(['开发', '管理', '运营', '推广'])}工作"
                }
                work_experience.append(job)
    
    # 添加当前工作
    work_experience.append({
        "company": f"某{random.choice(['科技', '教育', '医疗', '金融', '文化'])}公司",
        "position": current_occupation,
        "duration": "至今",
        "description": f"负责{random.choice(['项目', '产品', '服务'])}的{random.choice(['开发', '管理', '运营', '推广'])}工作"
    })
    
    return work_experience

def generate_psychological_traits(personality: List[str]) -> Dict:
    """生成心理特征"""
    traits = {
        "情绪稳定性": random.randint(1, 10),
        "外向性": random.randint(1, 10),
        "开放性": random.randint(1, 10),
        "宜人性": random.randint(1, 10),
        "尽责性": random.randint(1, 10)
    }
    
    # 根据性格特征调整心理特征
    if "开朗" in personality or "乐观" in personality:
        traits["情绪稳定性"] += 2
        traits["外向性"] += 2
    if "内向" in personality:
        traits["外向性"] -= 2
    if "理性" in personality:
        traits["尽责性"] += 2
    if "感性" in personality:
        traits["开放性"] += 2
    
    # 确保所有值在1-10之间
    for key in traits:
        traits[key] = max(1, min(10, traits[key]))
    
    return traits

def generate_all_personas(num_agents: int) -> Dict[str, Dict]:
    """生成所有agent的人设信息"""
    personas = {}
    for i in range(1, num_agents + 1):
        if i != 2:  # 跳过agent2（网警）
            agent_id = f"agent{i}"
            personas[agent_id] = generate_persona(agent_id)
    return personas

if __name__ == "__main__":
    # 生成100个agent的人设信息
    personas = generate_all_personas(100)
    
    # 打印示例
    for agent_id, persona in personas.items():
        print(f"\n{agent_id} 的人设信息:")
        print(f"性别: {persona['gender']}")
        print(f"年龄: {persona['age']}")
        print(f"居住地: {persona['location']}")
        print(f"职业: {persona['occupation']}")
        print(f"性格: {', '.join(persona['personality'])}")
        print(f"兴趣爱好: {', '.join(persona['interests'])}")
        print("\n教育背景:")
        for level, info in persona['education'].items():
            print(f"- {level}: {info['school']}, 专业: {info['major']}")
        print("\n工作经历:")
        for job in persona['work_experience']:
            print(f"- {job['company']}, {job['position']}, {job['duration']}")
        print("\n心理特征:")
        for trait, score in persona['psychological_traits'].items():
            print(f"- {trait}: {score}/10")
        print("\n上网聊天倾向:")
        for trait, value in persona['online_chat_traits'].items():
            if isinstance(value, list):
                print(f"- {trait}: {', '.join(value)}")
            else:
                print(f"- {trait}: {value}") 