# coding: utf-8
import requests
from bs4 import BeautifulSoup as bs

def parse_section(sections):
    content_str = ""
    for section in sections:
        if section.name is None:
            content_str += str(section)
        elif section.name in ["p", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6"]:
            tmp = "".join(child.text if hasattr(child, 'text') else str(child) for child in section.contents)
            content_str += tmp
        elif section.name == "a":
            tmp = f"{section.text.strip()} ({section['href']})"
            content_str += tmp
        elif section.name in ["strong", "em"]:
            tmp = f"<{section.name}>{section.text.strip()}</{section.name}>"
            content_str += tmp

    return content_str


def fetch_wechat_article(url, use_proxy=True):
    """
    resolve url (only for weixin)
    return a dict{'title', 'author', 'content'}
    """
    result = {}
    session = requests.Session()
    
    # User-Agent header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # set None without using proxy
    if not use_proxy:
        session.proxies = {
            "http": None,
            "https": None,
        }
    
    try:
        html = session.get(url, headers=headers, proxies={"http": None, "https": None})
        safe_content = html.text
        soup = bs(safe_content, "lxml")
        
        body = soup.find(class_="rich_media_area_primary_inner")
        title = body.find(class_="rich_media_title").text.strip()
        author = body.find(class_="rich_media_meta rich_media_meta_nickname").a.text.strip()
        content_p = body.find(class_="rich_media_content")
        # print(content_p)
        content_lst = content_p.contents

        content = parse_section(content_lst)

        result['title'] = title
        result['author'] = author
        result['content'] = content
    except Exception as e:
        print(f"Error occur while working at {url} : {e}")
    
    return result


# test
if __name__ == '__main__':
    # url = "https://mp.weixin.qq.com/s/0SUOXbpbybQgSvQh96cOAw"
    url = "https://mp.weixin.qq.com/s/HTbr7aOVuJoeqbYCpY-kTA"
    article = fetch_wechat_article(url, use_proxy=False)
    print(article['content'])