import json
import re
import time
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.bitable.v1 import *
from lark_oapi.api.authen.v1 import *
from resolve import fetch_wechat_article
from sumarize import get_from_content
import os
import time
from opt_db import insert_record
from tools import create_default_config, idea_match
from Idea_gen import generate_idea

# Global variable to store the last refresh time
# last_refresh_time = 0
# current_refresh_token = "initial refresh_token"

"""
refresh the user_access_token
params:
APP_ID, APP_SECRET
output:
user_access_token
"""
def refresh_user_access_token(APP_ID, APP_SECRET):
	global last_refresh_time, current_refresh_token

	client = lark.Client.builder() \
		.app_id(APP_ID) \
		.app_secret(APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	"""
	Request refresh user_access_token
	params:
	grant_type, refresh_token
	return refresh_token
	"""
	request: CreateRefreshAccessTokenRequest = CreateRefreshAccessTokenRequest.builder() \
		.request_body(CreateRefreshAccessTokenRequestBody.builder()
			.grant_type("refresh_token")
			.refresh_token(current_refresh_token)
			.build()) \
		.build()

	response: CreateRefreshAccessTokenResponse = client.authen.v1.refresh_access_token.create(request)

	if not response.success():
		lark.logger.error(
			f"client.authen.v1.refresh_access_token.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		
		"""
		Request get authorize code
		params:
		app_id, redirect_url
		return authorize code
		"""
		code_request: GetAuthorizeRequest = GetAuthorizeRequest.builder() \
			.app_id(APP_ID) \
			.redirect_uri("https://open.feishu.cn/api-explorer/cli_a4feb05323bcd013") \
			.build()
	
		code_response: GetAuthorizeResponse = client.authen.v1.authorize.get(code_request)
	
		if not code_response.success():
			lark.logger.error(
				f"client.authen.v1.authorize.get failed, code: {code_response.code}, msg: {code_response.msg}, log_id: {code_response.get_log_id()}")
			return

		code = code_response.data.code
		"""
		Request get user_access_token
		params:
		grant_type, code
		return refresh_token
		"""
		user_token_request: CreateOidcAccessTokenRequest = CreateOidcAccessTokenRequest.builder() \
			.request_body(CreateOidcAccessTokenRequestBody.builder()
				.grant_type("authorization_code")
				.code(code)
				.build()) \
			.build()
	
		user_token_response: CreateOidcAccessTokenResponse = client.authen.v1.oidc_access_token.create(user_token_request)
	
		# return while failed to get user_token_response
		if not user_token_response.success():
			lark.logger.error(
				f"client.authen.v1.oidc_access_token.create failed, code: {user_token_response.code}, msg: {user_token_response.msg}, log_id: {user_token_response.get_log_id()}")
			return

		current_refresh_token = user_token_response.data.refresh_token

		request: CreateRefreshAccessTokenRequest = CreateRefreshAccessTokenRequest.builder() \
			.request_body(CreateRefreshAccessTokenRequestBody.builder()
				.grant_type("refresh_token")
				.refresh_token(current_refresh_token)  # 使用当前的refresh_token
				.build()) \
			.build()

		response: CreateRefreshAccessTokenResponse = client.authen.v1.refresh_access_token.create(request)

	# last_refresh_time和current_refresh_token
	last_refresh_time = time.time()
	current_refresh_token = response.data.refresh_token  # 保存新的refresh_token
	print(f"refresh_token: {refresh_toekn}")

	return response.data.user_access_token

def fetch_messages_from_group(client, container_id, start_time, end_time):
	

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
			# tansform content into dict
			content_dict = json.loads(content)
			text = content_dict.get('text', '')
		except json.JSONDecodeError:
			# directly use content while failed
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
		app_id, app_secret, app_token, table_id):
	client = lark.Client.builder() \
		.app_id(app_id) \
		.app_secret(app_secret) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	"""
	Refresh the user_access_token
	"""
	# user_access_token = refresh_user_access_token(APP_ID=app_id, APP_SECRET=app_secret)
	# if not user_access_token:
	# 	lark.logger.error("Failed to refresh user_access_token.")
	# 	return None

	# build request
	request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
		.app_token(app_token) \
		.table_id(table_id) \
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

	# build response
	response: CreateAppTableRecordResponse = client.bitable.v1.app_table_record.create(request)

	if not response.success():
		lark.logger.error(
			f"client.bitable.v1.app_table_record.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return None

	print("Successfully create table record.")

	return

"""
main func
"""
@create_default_config
def News_collect():
	# get robot app_id and app_secret
	with open('config.txt', 'r', encoding='utf-8') as file:
		config = json.load(file)

	# set app_id, app_secret, Language
	app_id = config["app_id"]
	app_secret = config["app_secret"]
	container_id = config["container_id"]

	# set client
	client = lark.Client.builder() \
		.app_id(f"{app_id}") \
		.app_secret(f"{app_secret}").build()


	# init the last end time
	last_end_time = str(int(time.time()))

	while True:
		# 使用上次循环的结束时间作为这次循环的开始时间
		start_time = last_end_time
		# 获取当前时间作为这次循环的结束时间
		end_time = str(int(time.time()))

		# read config inf from config.txt
		with open('config.txt', 'r', encoding='utf-8') as file:
			config = json.load(file)

		app_token = config['app_token']
		table_id = config['table_id']

		data = fetch_messages_from_group(client=client, container_id=container_id, start_time=start_time, end_time=end_time)
		urls = extract_urls_from_messages(data)
		for url in urls:
			try:
				result = fetch_wechat_article(url=url)
				# print(f"result{result}")
				if result:

					"""
					All the data used
					"""
					summary, category, function, est_time = get_from_content(result['content'])
					title, ID_time, last_updated= result['title'], int(time.time()), int(time.time() * 1000)

					if summary is None or category is None or function is None:
						raise Exception

					print(f"{summary} \n{category} \n{function} \n{est_time}")
				time.sleep(5)

			except Exception as e:
				print(f"An error occurred while processing the URL {url}: {e}")

		# insert into database
			insert_record((ID_time, title, category, url, summary, last_updated, function, est_time))
		# create base table record with data
			create_app_table_record(content_type=category, summary=summary,file_link=url, \
				last_updated=last_updated,resource_name=title, \
				est_time=est_time, function=function, app_id=app_id, \
				app_secret=app_secret, app_token=app_token, table_id=table_id)
		# 保存这次循环的结束时间，以便下次循环使用
		last_end_time = end_time
		# 等待 30 秒
		time.sleep(30)

	return

@create_default_config
def Idea_gen_insert():
	idea, urls = generate_idea()
	idea_name, idea_description = idea_match(idea)
	content_type = "IDEA"
	last_updated = int(time.time() * 1000)
	with open('config.txt', 'r', encoding='utf-8') as file:
		config = json.load(file)

	app_id = config['app_id']
	app_secret = config['app_secret']
	app_token = config['app_token']
	table_id = config['table_id']

	client = lark.Client.builder() \
		.app_id(app_id) \
		.app_secret(app_secret) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# build request
	request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
		.app_token(app_token) \
		.table_id(table_id) \
		.request_body(AppTableRecord.builder()
			.fields({
					"内容类型": content_type,
					"文件链接": urls,
					"最近更新": last_updated,
					"产品名称": idea_name,
					"产品描述": idea_description
				})
			.build()) \
		.build()

	# build response
	response: CreateAppTableRecordResponse = client.bitable.v1.app_table_record.create(request)

	if not response.success():
		lark.logger.error(
			f"client.bitable.v1.app_table_record.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return None

	print("Successfully create table record for idea.")

	return


# test the process for collecting news
if __name__ == "__main__":
	# Idea_gen_insert()
	News_collect()
	





