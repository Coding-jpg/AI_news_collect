import os
import re
import json

"""
NOTE: for decoration, regulation match
"""

"""
decorate : generate the default config
"""
def create_default_config(func):
	def wrapper(*args, **kwargs):
		if not os.path.exists('config.txt'):
			default_config = {
				"Language": "Chinese",
				"Prompt": "Please provide a summary in 300 characters and specify the category into one of the following categories: '{categories}'. Additionally, it identifies the function mentioned in the content based on its context. Give the response in the format 'Summary: 内容 (Category: 分类) (Function: 功能) '. The content and function should be {Language}.",
				"Categories": ["text", "video", "music", "agent"],
				"Openai_Key": "",
				"app_id": "",
				"app_secret": "",
				"container_id": "",
				"app_token": "",
				"table_id": ""
			}
			with open('config.txt', 'w', encoding='utf-8') as file:
				json.dump(default_config, file, ensure_ascii=False, indent=4)
			print("Successfully create default config.")
			
		func_result = func(*args, **kwargs)
		return func_result
	return wrapper

"""
regulation match for idea
"""
def idea_match(text:str) -> str:
	product_name_match = re.search(r'产品名称：(.*?\n)(?=产品描述|$)', text)
	product_description_match = re.search(r'产品描述：(.*)', text)

	if product_name_match and product_description_match:
		product_name = product_name_match.group(1).strip()
		product_description = product_description_match.group(1).strip()
		# print(f"产品名称: {product_name}\n产品描述: {product_description}")
	else:
		product_name = None
		product_description = None
		# print(f"Failed to match.")

	return product_name, product_description


if __name__ == "__main__":
	# idea_match test
	text = '产品名称：创意设计助手\n产品描述：结合设计机器人和文本处理技术，为用户提供创意设计方案和文案撰写，帮助用户快速完成设计任务。'
	idea_match(text)