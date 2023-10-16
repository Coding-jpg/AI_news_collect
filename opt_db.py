import sqlite3
import time
from typing import Tuple

"""
connect database
"""
# conn = sqlite3.connect("News_base.db")
# cur = conn.cursor()

"""
create table
ID -> time stamp
"""
# cur.execute("""
# 	CREATE TABLE News(
# 		ID INTEGER PRIMARY KEY,
# 		title TEXT,
# 		content_type TEXT, 
# 		url TEXT,
# 		summary TEXT,
# 		last_update INTEGER,
# 		function TEXT,
# 		est_time INTEGER)
# 	""")

"""
process
"""

# insert case

# news = [
# 	(int(time.time()), 
# 	'最多400万token上下文、推理提速22倍，StreamingLLM火了，已获GitHub 2.5K星',
# 	'text',
# 	'https://mp.weixin.qq.com/s/qIwYJAfD5bXJS6j0xtp2cw',
# 	'研究者们提出了一种名为「StreamingLLM」的方法，使语言模型能够流畅地处理无穷无尽的文本。StreamingLLM利用了注意力池具有高注意力值的特点，通过保留注意力池token的KV值和滑动窗口的KV值来锚定注意力计算并稳定模型的性能。使用StreamingLLM，模型可以可靠地模拟400万个token，速度提高了22.2倍，而没有损耗性能。',
# 	'处理无穷无尽的文本',
# 	10
# 		),
# ]

# cur.executemany("""
# 	INSERT INTO News VALUES (?,?,?,?,?,?,?)

# 	""", news)


# select case

# news_record = cur.execute("""
# 	SELECT * FROM News
# 	""")

# print(news_record.fetchone())
def select_record() -> str:

	try:
		conn = sqlite3.connect("News_base.db")
		cur = conn.cursor()
		cur.execute("""
				SELECT * FROM News
			""")
		result = cur.fetchall()

	except Exception as e:
		result = None
		print(f"Failed to select record: {e}")
		
	return result


"""
insert the record from create_app_table_record
params:
record: (ID, title, content_type, url, summary, function, est_time)
return: warning inf
"""
def insert_record(record: Tuple[int, str, str, str, str, str, str, int]) -> str:

	try:
		conn = sqlite3.connect("News_base.db")
		cur = conn.cursor()
		cur.execute("""
			INSERT INTO News VALUES (?,?,?,?,?,?,?,?)
			""", record)
		conn.commit()
		conn.close()

	except Exception as e:
		print(f"Failed to insert record: {e}")

	print("insert_record finished. ")

	return 0

def random_select_record():

	try:
		conn = sqlite3.connect("News_base.db")
		cur = conn.cursor()
		cur.execute("""
			SELECT function, url FROM News ORDER BY RANDOM() LIMIT 3;
			""")
		conn.commit()
		result = cur.fetchall()
		conn.close()

		functions = [f[0] for f in result]
		urls = [u[1] for u in result]

	except Exception as e:
		print(f"Failed to select record: {e}")

	return functions, urls

if __name__ == "__main__":
	data1 = (int(time.time()), "最多400万token上下文、推理提速22倍，StreamingLLM火了，已获GitHub 2.5K星", \
					"text", "https://mp.weixin.qq.com/s/qIwYJAfD5bXJS6j0xtp2cw", \
					"研究者们提出了一种名为「StreamingLLM」的方法，使语言模型能够流畅地处理无穷无尽的文本。StreamingLLM利用了注意力池具有高注意力值的特点，通过保留注意力池token的KV值和滑动窗口的KV值来锚定注意力计算并稳定模型的性能。使用StreamingLLM，模型可以可靠地模拟400万个token，速度提高了22.2倍，而没有损耗性能。", \
					int(time.time() * 1000), "处理无穷无尽的文本", 10)
	data2 = (int(time.time()), "在笔记本电脑上从头设计一款会走路的机器人，AI只需26秒", 
					"text", "https://mp.weixin.qq.com/s/SRH9iLaEttv5kWgeFdRlYQ", \
					"由西北大学研究人员领导的一个团队开发了可以从头开始设计机器人的AI，整个设计过程只用了26秒，AI自己领悟了「长腿」是穿越陆地的好方法。这个AI可以帮助解决设计机器人的难题，为人们创造新的可能性和演进道路。", \
					int(time.time() * 1000), "设计机器人", 10)
	# insert_record(data2)
	# print(select_record())
	f, u = random_select_record()
	print(f"function: {f}, url: {u}")