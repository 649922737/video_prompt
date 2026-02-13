import requests
import json
import os

class JimengAgent:
    def __init__(self, api_key, endpoint):
        self.api_key = api_key
        self.endpoint = endpoint
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _read_file(self, filename, default=""):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read() if filename.endswith('.txt') else json.load(f)
        return default

    def generate(self, user_query, img_num=0, vid_num=0):
        # 1. 加载配置和知识库 (RAG 核心)
        config = self._read_file('agent_skills.json', {"role": "AI Assistant", "syntax_rules": []})
        examples = self._read_file('examples.txt', "")
        
        # 2. 自动构建素材标签
        asset_tags = [f"@图片{i+1}" for i in range(img_num)] + [f"@视频{i+1}" for i in range(vid_num)]
        asset_str = "，".join(asset_tags) if asset_tags else "纯文字，无参考素材"

        # 3. 组装 System Prompt
        system_msg = f"""
        # Role: {config['role']}
        # Rules:
        {chr(10).join(config['syntax_rules'])}
        
        # RAG Reference Examples:
        {examples}
        
        # Current Task:
        用户描述: {user_query}
        素材引用: {asset_str}
        请输出符合 Seedance 2.0 语法的详细分镜提示词。
        """

        payload = {
            "model": "gemini-3-pro", 
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.3
        }

        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"执行失败: {str(e)}"

# --- 修改后的 Main 函数 ---
if __name__ == "__main__":
    MY_KEY = ""
    MY_URL = ""
    
    agent = JimengAgent(MY_KEY, MY_URL)
    
    print("="*50)
    print("🎬 即梦 Seedance 2.0 分镜提示词助手")
    print("请输入您的视频构想（支持多行），输入 'end' 并回车结束输入：")
    print("="*50)

    # 多行输入逻辑
    user_lines = []
    while True:
        line = input()
        if line.strip().lower() == 'end':
            break
        user_lines.append(line)
    
    full_query = "\n".join(user_lines)

    if not full_query.strip():
        print("未输入有效内容，程序退出。")
    else:
        # 这里你可以根据需要手动修改图片和视频的数量
        img_n = int(input("请输入参考图片数量 (0-12): ") or 0)
        vid_n = int(input("请输入参考视频数量 (0-12): ") or 0)
        
        print("\n🚀 正在为您策划导演级分镜，请稍候...\n")
        result = agent.generate(full_query, img_num=img_n, vid_num=vid_n)
        
        print("-" * 30 + " 生成结果 " + "-" * 30)
        print(result)
        print("-" * 70)
