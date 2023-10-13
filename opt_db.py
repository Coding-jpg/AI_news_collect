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


"""
insert the record from create_app_table_record
params:
record: (ID, title, content_type, url, summary, function, est_time)
return: warning inf
"""
def insert_record(record: Tuple[int, str, str, str, str, str, str, int]) -> str:

	try:
		conn = sqlite3.connect("News_base.db")
		cur = con.cursor()
		cur.execute("""
			INSERT INTO News VALUES (?,?,?,?,?,?,?,?)
			""", record)
		conn.commit()
		conn.close()

	except Exception as e:
		print(f"Failed to insert record: {e}")

	return "insert_record finished. "

def random_select_record():

	try:
		conn = sqlite3.connect("News_base.db")
		cur = con.cursor()
		cur.execute("""
			SELECT function FROM News ORDER BY RANDOM() LIMIT 3;
			""")
		conn.commit()
		function = cur.fetchall()
		conn.close()


	except Exception as e:
		print(f"Failed to select record: {e}")

	return function

# if __name__ == "__main__":
	# insert_record()