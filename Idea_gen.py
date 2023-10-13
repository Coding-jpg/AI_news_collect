from opt_db import random_select_record
import openai
import re
import os
import json

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'  
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'  

def generate_idea(function_list: list) -> str:
	with open('config.txt', 'r', encoding='utf-8') as file:
		config = json.load(file)

	openai.api_key = config["Openai_Key"]
	system_content = config["idea_system_content"]
	user_content = str(function_list)

	model_name = "gpt-3.5-turbo"

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

	idea = response.get('choices')[0].get('message').get('content')

	return idea


"""
test case
"""
if __name__ == "__main__":
	function_list = ['Text to Speech','Chat robot','Text to Image']
	print(generate_idea(function_list))


