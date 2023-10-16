# -*- coding: utf-8 -*-
import os
import openai
import re
import json
import jieba

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'  
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'  

def get_from_content(user_content):
	# count the tokens for different models
	read_rate = 150
	text_len = len(list(jieba.cut(user_content)))
	model_name = 'gpt-3.5-turbo'

	# check if sth wrong with conten
	if text_len < 5:
		return None, None, None, None

	print(f"token length： {text_len}")

	# estimated time for reading
	est_time = f"{text_len // read_rate}"
	print(f"estimated time for reading: {est_time}分钟.")

	# get config from config.txt
	with open('config.txt', 'r', encoding='utf-8') as file:
		config = json.load(file)

	# set Openai api key
	openai.api_key = config["Openai_Key"]

	categories_str = "', '".join(config["Categories"])
	system_content = config["Prompt"].replace("{categories}", categories_str).replace("{Language}", config["Language"])

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
	# print(assistant_content)
	
	Summary_pat = r"Summary:\s(.*?)(?=\(Category:)"
	Category_pat = r"\(Category:(.*?)\)(?=\s\(Function:)"
	Function_pat = r"\(Function:([^)]+)"

	# regular expression
	Summary_match = re.search(Summary_pat, assistant_content)
	Category_match = re.search(Category_pat, assistant_content)
	Function_match = re.search(Function_pat, assistant_content)
	
	if Summary_match and Category_match and Function_match: 
		# 提取匹配到的内容
		print("Successfully Match !")
		summary = Summary_match.group(1)
		category = Category_match.group(1)
		function = Function_match.group(1)
		# print("Summary:", summary)
		# print("Category:", category)
		# print("Function:", function)
	else:
		print("Failed to match......")
		return None, None, None, None

	# check name
	model_name = 'gpt-3.5-turbo'

	return summary, category, function, est_time



# 测试函数
if __name__ =="__main__":
	user_content = "多模态大模型最全综述来了！由微软 7 位华人研究员撰写，足足 119 页——它从目前已经完善的 和还处于最前沿的两类多模态大模型研究方向出发，全面总结了五个具体研究主题：并重点关注到 一个现象：Ps. 这也是为什么论文开头作者就直接画了一个哆啦 A 梦的形象。谁适合阅读这份综述（报告）？用微软的原话来说：只要你想学习多模态基础模型的基础知识和最新进展，不管你是专 业研究员，还是在校学生，它都是你的「菜」。一起来看看～论文完整编译版本参见：微软多模态 大模型综述--多模态基础模型：从专家到通用助手，第一章‍微软多模态大模型综述--多模态基础模型：从专家到通用助手，第二章微软多模态大模型综述--多模态基础模型：从专家到通用助手，第 三章：视觉生成01视觉理解这五个具体主题中的前 2 个为目前已经成熟的领域，后 3 个则还属于 前沿领域。这部分的核心问题是如何预训练一个强大的图像理解 backbone。如下图所示，根据用于训练模型的监督信号的不同，我们可以将方法分为三类：标签监督、语言监督（以 CLIP 为代表） 和只有图像的自监督。其中最后一个表示监督信号是从图像本身中挖掘出来的，流行的方法包括对 比学习、非对比学习和 masked image 建模。在这些方法之外，文章也进一步讨论了多模态融合、 区域级和像素级图像理解等类别的预训练方法。还列出了以上这些方法各自的代表作品。02视觉生 成这个主题是 AIGC 的核心，不限于图像生成，还包括视频、3D 点云图等等。并且它的用处不止于艺术、设计等领域——还非常有助于合成训练数据，直接帮助我们实现多模态内容理解和生成的闭 环。在这部分，作者重点讨论了生成与人类意图严格一致的效果的重要性和方法（重点是图像生成 ）。具体则从空间可控生成、基于文本再编辑、更好地遵循文本提示和生成概念定制（concept customization）四个方面展开。在本节最后，作者还分享了他们对当前研究趋势和短期未来研究方向 的看法。即，开发一个通用的文生图模型，它可以更好地遵循人类的意图，并使上述四个方向都能 应用得更加灵活并可替代。同样列出了四个方向的各自代表作：03统一视觉模型这部分讨论了构建 统一视觉模型的挑战：一是输入类型不同；二是不同的任务需要不同的粒度，输出也要求不同的格 式；三是在建模之外，数据也有挑战。比如不同类型的标签注释成本差异很大，收集成本比文本数 据高得多，这导致视觉数据的规模通常比文本语料库小得多。不过，尽管挑战多多，作者指出：CV 领域对于开发通用、统一的视觉系统的兴趣是越来越高涨，还衍生出来三类趋势：一是从闭集（closed-set）到开集（open-set），它可以更好地将文本和视觉匹配起来。二是从特定任务到通用能力，这个转变最重要的原因还是因为为每一项新任务都开发一个新模型的成本实在太高了；三是从静 态模型到可提示模型，LLM 可以采用不同的语言和上下文提示作为输入，并在不进行微调的情况下 产生用户想要的输出。我们要打造的通用视觉模型应该具有相同的上下文学习能力。04LLM 加持的 多模态大模型本节全面探讨多模态大模型。先是深入研究背景和代表实例，并讨论 OpenAI 的多模 态研究进展，确定该领域现有的研究空白。接下来作者详细考察了大语言模型中指令微调的重要性 。再接着，作者探讨了多模态大模型中的指令微调工作，包括原理、意义和应用。最后，涉及多模 态模型领域中的一些高阶主题，方便我们进行更深入的了解，包括：更多超越视觉和语言的模态、 多模态的上下文学习、参数高效训练以及 Benchmark 等内容。05多模态 agent所谓多模态 agent，就是一种将不同的多模态专家与 LLM 联系起来解决复杂多模态理解问题的办法。这部分，作者主要先带大家回顾了这种模式的转变，总结该方法与传统方法的根本差异。然后以 MM-REACT 为代表带 大家看了这种方法的具体运作方式。接着全面总结了如何构建多模态 agent，它在多模态理解方面 的新兴能力，以及如何轻松扩展到包含最新、最强的 LLM 和潜在的数百万种工具中。当然，最后也是一些高阶主题讨论，包括如何改进/评估多多模态 agent，由它建成的各种应用程序等。06作者介绍本报告一共 7 位作者。发起人和整体负责人为 Chunyuan Li。他是微软雷德蒙德首席研究员，博士毕业于杜克大学，最近研究兴趣为 CV 和 NLP 中的大规模预训练。他负责了开头介绍和结尾总结以及「利用 LLM 训练的多模态大模型」这章的撰写。核心作者一共 4 位：目前已进入 Apple AI/ML 工作，负责大规模视觉和多模态基础模型研究。此前是 Microsoft Azure AI 的首席研究员，北 大本硕毕业，杜克大学博士毕业。微软高级研究员，罗切斯特大学博士毕业，获得了 ACM SIGMM 杰出博士奖等荣誉，本科就读于中科大。微软雷德蒙德研究院深度学习小组首席研究员。佐治亚理工 学院博士毕业。Microsoft Cloud & AI 计算机视觉组研究员，普渡大学硕士毕业。他们分别负责了剩下四个主题章节的撰写。综述地址：https://arxiv.org/abs/2309.10020 "
	summary, category, function, est_time= get_from_content(user_content)
	print(f"{summary} {category} {function} {est_time}")
