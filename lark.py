import json
import re
import time
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.bitable.v1 import *
from lark_oapi.api.authen.v1 import *
from beatiful_soup import fetch_wechat_article
from sumarize import get_from_content
import os
import time

# Global variable to store the last refresh time
last_refresh_time = 0
current_refresh_token = "初始的refresh_token"

def refresh_user_access_token(APP_ID, APP_SECRET):
	global last_refresh_time, current_refresh_token

	client = lark.Client.builder() \
		.app_id(APP_ID) \
		.app_secret(APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	request: CreateRefreshAccessTokenRequest = CreateRefreshAccessTokenRequest.builder() \
		.request_body(CreateRefreshAccessTokenRequestBody.builder()
			.grant_type("refresh_token")
			.refresh_token(current_refresh_token)  # 使用当前的refresh_token
			.build()) \
		.build()

	response: CreateRefreshAccessTokenResponse = client.authen.v1.refresh_access_token.create(request)

	if not response.success():
		lark.logger.error(
			f"client.authen.v1.refresh_access_token.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return None

	# 更新last_refresh_time和current_refresh_token
	last_refresh_time = time.time()
	current_refresh_token = response.data.refresh_token  # 保存新的refresh_token

	return response.data.user_access_token

# ... [rest of your code]

	user_access_token = refresh_user_access_token(APP_ID=app_id, APP_SECRET=app_secret)
	if not user_access_token:
		lark.logger.error("Failed to refresh user_access_token.")
		return None

def fetch_messages(client, container_id, start_time, end_time):
	

	# 构造请求对象
	request: ListMessageRequest = ListMessageRequest.builder() \
		.container_id_type("chat") \
		.container_id(container_id) \
		.start_time(start_time) \
		.end_time(end_time) \
		.sort_type("ByCreateTimeDesc") \
		.build()

	# 发起请求
	response: ListMessageResponse = client.im.v1.message.list(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.im.v1.message.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return None

	# 处理业务结果
	# lark.logger.info(lark.JSON.marshal(response.data, indent=4))
	return response.data

"""
extract urls from each message
"""
def extract_urls_from_messages(response_body):
	url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
	urls = []

	items = response_body.items if hasattr(response_body, 'items') else []
	for item in items:
		content = item.body.content if hasattr(item.body, 'content') else ''
		try:
			# 尝试将 content 转换为字典
			content_dict = json.loads(content)
			text = content_dict.get('text', '')
		except json.JSONDecodeError:
			# 如果转换失败，直接使用 content
			text = content

		# 使用正则表达式找到所有的 URL
		found_urls = url_pattern.findall(text)
		urls.extend(found_urls)
	return urls

"""
create a new record in feishu table
"""
def create_app_table_record(content_type, summary, file_link, \
		last_updated, resource_name, est_time, function, \
		app_id, app_secret):
	client = lark.Client.builder() \
		.enable_set_token(True) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()


	# Refresh the user_access_token
	# user_access_token = refresh_user_access_token(APP_ID=app_id, APP_SECRET=app_secret)
	# if not user_access_token:
	# 	lark.logger.error("Failed to refresh user_access_token.")
	# 	return None

	user_access_token = 'u-fx95vXe2J26pLhzML4nHhQh5hjNxl0pbMW00g5e00AL4'

	request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
		.app_token("I3PdbCcDkakWERsLWMucXKygnNh") \
		.table_id("tblS1FNmOKM4rPlT") \
		.request_body(AppTableRecord.builder()
			.fields({
				"内容类型": content_type,
				"摘要": summary,
				"文件链接": file_link,
				"最近更新": last_updated,
				"资料名称": resource_name,
				"功能": function,
				"原文估计阅读时间": est_time+"分钟"
			})
			.build()) \
		.build()

	option = lark.RequestOption.builder().user_access_token("u-fx95vXe2J26pLhzML4nHhQh5hjNxl0pbMW00g5e00AL4").build()
	response: CreateAppTableRecordResponse = client.bitable.v1.app_table_record.create(request, option)

	if not response.success():
		lark.logger.error(
			f"client.bitable.v1.app_table_record.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return None

	# lark.logger.info(lark.JSON.marshal(response.data, indent=4))
	return response.data

if __name__ == "__main__":
	# get robot app_id and app_secret
	if not os.path.exists('config.txt'):
		default_config = {
			"Language": "English",
			"Prompt": "You are an assistant that summarizes content in {Language} and categorizes it into one of the following categories: '{categories}'. Please provide a summary in 150 characters and specify the category. Additionally, it identifies the function in {Language} mentioned in the content based on its context. Give the response in the format 'Summary:content (Category:\"\") (Function: \"\") '.",
			"Categories": ["text", "video", "music", "agent"],
			"Openai_Key": "",
			"app_id": "",
			"app_secret": "",
			"container_id": ""
		}
		with open('config.txt', 'w', encoding='utf-8') as file:
			json.dump(default_config, file, ensure_ascii=False, indent=4)

	# read config
	with open('config.txt', 'r', encoding='utf-8') as file:
		config = json.load(file)

	# set app_id, app_secret
	app_id = config["app_id"]
	app_secret = config["app_secret"]
	container_id = config["container_id"]

	# set client
	client = lark.Client.builder() \
		.app_id(f"{app_id}") \
		.app_secret(f"{app_secret}").build()


	# 初始化上次循环的结束时间为当前时间
	last_end_time = str(int(time.time()))

	# last_end_time = '1696089240'

	while True:
		# 使用上次循环的结束时间作为这次循环的开始时间
		start_time = last_end_time
		# 获取当前时间作为这次循环的结束时间
		end_time = str(int(time.time()))

		data = fetch_messages(client=client, container_id=container_id, start_time=start_time, end_time=end_time)
		urls = extract_urls_from_messages(data)
		for url in urls:
			try:
				result = fetch_wechat_article(url=url)
				# print(f"result{result}")
				if result:
					summary, category, function, est_time = get_from_content(result['content'])
					if summary is None or category is None or function is None:
						raise Exception

					print(f"{summary} \n{category} \n{function} \n{est_time}")
				time.sleep(5)

			except Exception as e:
				print(f"An error occurred while processing the URL {url}: {e}")
		# 写入多维表
			create_app_table_record(content_type=category, summary=summary,file_link=url, \
				last_updated=int(time.time() * 1000),resource_name=result['title'], \
				est_time=est_time, function=function, app_id=app_id, \
				app_secret=app_secret)
		# 保存这次循环的结束时间，以便下次循环使用
		last_end_time = end_time
		# 等待 30 秒
		time.sleep(30)





