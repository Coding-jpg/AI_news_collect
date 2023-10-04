import os
import openai
import re

openai.api_key = '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'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'  
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'  

import json
import re
import os

def get_from_content(user_content):
    # 检查是否存在config.txt文件
    if not os.path.exists('config.txt'):
        default_config = {
            "Language": "English",
            "Prompt": "You are an assistant that summarizes content in {Language} and categorizes it into one of the following categories: '{categories}'. Please provide a summary in 150 characters and specify the category. Additionally, it identifies the function in {Language} mentioned in the content based on its context. Give the response in the format 'Summary:content (Category:\"\") (Function: \"\") '.",
            "Categories": ["text", "video", "music", "agent"]
        }
        with open('config.txt', 'w', encoding='utf-8') as file:
            json.dump(default_config, file, ensure_ascii=False, indent=4)

    # 从config.txt中读取配置
    with open('config.txt', 'r', encoding='utf-8') as file:
        config = json.load(file)

    categories_str = "', '".join(config["Categories"])
    system_content = config["Prompt"].replace("{categories}", categories_str).replace("{Language}", config["Language"])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        temperature=0.01,
        max_tokens=1024,
        top_p=0.01,
        frequency_penalty=0,
        presence_penalty=0
    )

    # 提取 assistant 的回复内容
    assistant_content = response.get('choices')[0].get('message').get('content')

    # 使用正则表达式来分割摘要、类别、功能
    match = re.match(r'Summary: (.*?) \(Category: (.*?)\) \(Function: (.*?)\)$', assistant_content)

    if match:
        summary = match.group(1)
        category = match.group(2)
        function = match.group(3)
    else:
        # 提供默认值或抛出错误
        summary = assistant_content
        category = "Unknown"
        function = "Unknown"

    return summary, category, function



# 测试函数
if __name__ =="__main__":
    user_content = "市场对 AI Agent 的期望一直很高，除了各种单向任务的 Agent 外，之前斯坦福大学和 Google 的一项实验已经展示了由 25 个 AI Agent 自行协同运行的虚拟城镇（Virtual Town），它们在这个虚拟城镇里制定每日的日程、约会以及策划一些活动聚会。\
不过最新的一项研究实验，他们创建了一家叫 ChatDev 的虚拟公司，由 7 个 AI Agent 组成，角色分别是 CEO、CTO、CPO 、程序员、设计师、测试员以及代码评审，这些 Agent 由 ChatGPT 3.5 的模型支持。"
    summary, category, function = get_from_content(user_content)
