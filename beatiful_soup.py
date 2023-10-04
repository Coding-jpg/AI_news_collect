# coding: utf-8
import requests
from bs4 import BeautifulSoup as bs

def parse_section(sections):
    content = ""
    for section in sections:
        if section.name is None:
            content += section
        elif section.name == "p":
            tmp = "".join(content.text if hasattr(content, 'text') else str(content) for content in section.contents)
            content += tmp
        else:
            print(f"Unhandled tag: {section.name}")
    return content

def fetch_wechat_article(url, use_proxy=True):
    result = {}
    session = requests.Session()
    
    # �����ʹ�ô�������session�Ĵ���ΪNone
    if not use_proxy:
        session.proxies = {
            "http": None,
            "https": None,
        }
    
    try:
        html = session.get(url, proxies={"http": None, "https": None})  # ʹ��session.get()����requests.get()
        soup = bs(html.text, "lxml")
        
        body = soup.find(class_="rich_media_area_primary_inner")
        title = body.find(class_="rich_media_title").text.strip()
        author = body.find(class_="rich_media_meta rich_media_meta_nickname").a.text.strip()
        content_p = body.find(class_="rich_media_content")
        content_lst = content_p.contents

        content = parse_section(content_lst)

        result['title'] = title
        result['author'] = author
        result['content'] = content
    except Exception as e:
        print(f"Error occur while working at {url} : {e}")
    
    return result

# ���Ժ���
if __name__ == '__main__':
    url = "https://mp.weixin.qq.com/s/hm5widzIJoPI29kEcpcwdQ"
    article = fetch_wechat_article(url, use_proxy=False)  # ����use_proxyΪFalse��ȡ������
    print(article)