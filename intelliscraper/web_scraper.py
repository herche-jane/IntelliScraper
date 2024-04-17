import json
import re

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

import json
import re
from bs4 import BeautifulSoup, Tag
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import clean_text, get_most_similar_element, find_element_by_path


class WebScraper:
    def __init__(self,wanted_list, url=None, proxy=None, html=None, role_path=None,save_path=None,example_element=None, element_regex=None,max_reasult=None,similarity=0.5):
        """
             初始化 WebScraper 类的实例。

             :param wanted_list: 需要找到的元素的列表。
             :param url: 要抓取的网页的 URL。
             :param proxy: 使用的代理地址。
             :param html: 直接提供的 HTML 内容。
             :param role_path: 保存规则的文件路径。
             :param save_path: 保存结果的文件路径。
             """
        if len(wanted_list) > 1:
            raise ValueError("wanted_list can only be one.")
        self.url = url
        self.proxy = proxy
        self.html = html
        self.wanted_list = wanted_list
        self.role_path = role_path
        self.save_path = save_path
        self.max_reasult = max_reasult
        self.similarity = similarity
        self.example_element = example_element
        self.element_regex = element_regex
        if self.url:
            self.html = self.fetch_data_with_requests()

    def find_all_element_paths(self):
        """
               在 HTML 中查找所有 wanted_list 中的元素的路径。
               :return: 返回一个字典，其中包含 wanted_list 中每个元素的所有路径。
               """
        if not self.html:
            raise ValueError("HTML content is not provided or fetched.")
        soup = BeautifulSoup(self.html, 'html.parser')
        cleaned_wanted_list = {clean_text(item): item for item in self.wanted_list}  # 创建一个映射，清洁文本到原始文本
        stack_list = {item: set() for item in self.wanted_list}  # 为每个wanted_list项初始化一个空集合

        def search_element_paths(element, path):
            if isinstance(element, Tag):
                new_path = path + ' -> ' + element.name + str(element.attrs)
                for child in element.children:
                    search_element_paths(child, new_path)
            elif isinstance(element, NavigableString):
                cleaned_element_text = clean_text(element)
                for cleaned_text, original_text in cleaned_wanted_list.items():
                    if cleaned_text in cleaned_element_text:
                        stack_list[original_text].add(path.strip(' -> '))

        search_element_paths(soup, '')
        return stack_list



    def fetch_data_with_requests(self):
        """
              使用请求从 URL 获取 HTML 内容。
              :return: 返回从网页获取的 HTML 内容。
              """
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        # 设置请求头
        headers = {
            "User-Agent": user_agent
        }
        # 设置代理
        proxies = None
        if self.proxy:
            proxies = {
                "http": self.proxy,
                "https":self.proxy
            }
        try:
            response = requests.get(self.url, headers=headers, proxies=proxies, timeout=10)
            if response.status_code == 200:
                return response.content
        except requests.RequestException as e:
            print(f"请求错误: {e}")
        return None




    def build(self):
        """
             构建并返回从 HTML 中找到的元素。
             :return: 返回找到的元素列表。
             """
        elements = []
        if self.url:
            self.html = self.fetch_data_with_requests()
        role_json = None
        if self.role_path:
            with open(self.role_path, 'r', encoding='utf-8') as file:
                rule_json_str = file.read()
                role_json = json.loads(rule_json_str)
        else:
            stack_list = self.find_all_element_paths()
            # 将层级路径转换为JSON格式
            json_stack_list = {text: list(paths) for text, paths in stack_list.items()}
            role_json = json.dumps(json_stack_list, ensure_ascii=False, indent=4)
            if self.save_path:
                with open(self.save_path, 'w', encoding='utf-8') as file:
                     json.dump(role_json, file, ensure_ascii=False)
        results = get_most_similar_element(self.html, role_json, self.max_reasult, self.similarity)
        for result in results:
             element = find_element_by_path(self.html, result)
             if element:
                 normalized_element = self.normalize_element(str(element), self.element_regex)
                 if normalized_element:
                     elements.append(normalized_element)
        return elements

    def normalize_element(self,html_content, element_regex):
        """
        Normalize a given HTML element string using a regex pattern.
        Extracts and returns the portion of the HTML that matches the regex.

        :param html_content: The HTML content string of an element.
        :param element_regex: Regex pattern to apply for normalization.
        :return: A normalized or extracted part of the HTML element, or None if no match is found.
        """
        match = re.search(element_regex, html_content)
        if match:
            result = match.group()
            print(result)
            return result  # Return the matched part of the HTML
        return None  # Return None if no match is found






