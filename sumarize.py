import os
import openai
import re
import json
import jieba

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'  
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'  

def get_from_content(user_content):
	# count the tokens for different models
	text_len = len(list(jieba.cut(user_content)))
	model_name = 'gpt-3.5-turbo'

	# check if sth wrong with conten
	if text_len < 5:
		return None, None, None

	# get config from config.txt
	with open('config.txt', 'r', encoding='utf-8') as file:
		config = json.load(file)

	# set Openai api key
	openai.api_key = config["Openai_Key"]

	categories_str = "', '".join(config["Categories"])
	system_content = config["Prompt"].replace("{categories}", categories_str).replace("{Language}", config["Language"])

	print(f"token长度： {text_len}")

	if text_len > 2500:
		model_name = 'gpt-3.5-turbo-16k'

	print(f"The current model : {model_name}")

	response = openai.ChatCompletion.create(
		model=f"{model_name}",
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
	# 使用正则表达式匹配内容

	pattern = r"Summary: (.*?) \(Category: (.*?)\) \(Function: (.*?)\)"
	
	match = re.search(pattern, assistant_content)
	if match:
	    summary = match.group(1)
	    category = match.group(2)
	    function = match.group(3)
	    # print("Summary:", summary)
	    # print("Category:", category)
	    # print("Function:", function)
	else:
	    print("文本不匹配给定的格式。")
	    return None, None, None

	# check name
	model_name = 'gpt-3.5-turbo'

	return summary, category, function



# 测试函数
if __name__ =="__main__":
	user_content = "作者们提出了基于大模型的智能代理通用框架，该框架由控制端、感知端和行动端组成。智能代理需要具备认知能力，感知和应对外界变化，类似于人类在社会中生存所需的适应能力。"
	summary, category, function = get_from_content(user_content)
	# print(f"{summary} {category}")
