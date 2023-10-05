import json
import re
import time
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.bitable.v1 import *
from beatiful_soup import fetch_wechat_article
from sumarize import get_from_content
import os


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

def create_app_table_record(content_type, summary, file_link, last_updated, resource_name):
	client = lark.Client.builder() \
		.enable_set_token(True) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
		.app_token("I3PdbCcDkakWERsLWMucXKygnNh") \
		.table_id("tblS1FNmOKM4rPlT") \
		.request_body(AppTableRecord.builder()
			.fields({
				"内容类型": content_type,
				"摘要": summary,
				"文件链接": file_link,
				"最近更新": last_updated,
				"资料名称": resource_name
			})
			.build()) \
		.build()

	option = lark.RequestOption.builder().user_access_token("u-fltTXu9DVdHFLCkJ3jkdRulgnbJR40NHNG00k4Ma0Jag").build()
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

	# set client
	client = lark.Client.builder() \
		.app_id(f"{app_id}") \
		.app_secret(f"{app_secret}").build()

	container_id = config["container_id"]

	# 初始化上次循环的结束时间为当前时间
	# last_end_time = str(int(time.time()))
	# 9月25日0:00 时间戳
	last_end_time = '1689964800'
	while True:
		# 使用上次循环的结束时间作为这次循环的开始时间
		start_time = last_end_time
		# 获取当前时间作为这次循环的结束时间
		end_time = str(int(time.time()))
		# 9月25日24：00 时间戳
		# end_time = 1690051200

		data = fetch_messages(client=client, container_id=container_id, start_time=start_time, end_time=end_time)
		urls = extract_urls_from_messages(data)
		for url in urls:
			try:
				result = fetch_wechat_article(url=url)
				# print(f"result{result}")
				if result:
					summary, category, function = get_from_content(result['content'])
					if summary==None // category==None // function==None:
						break

					print(f"{summary} \n{category} \n{function}")
				time.sleep(5)

			except Exception as e:
				print(f"An error occurred while processing the URL {url}: {e}")
				# create_app_table_record(content_type='', summary=summary,file_link=url, last_updated=int(time.time() * 1000),resource_name=result['title'])
		# 保存这次循环的结束时间，以便下次循环使用
		last_end_time = end_time

		# 等待 30 秒
		time.sleep(30)





