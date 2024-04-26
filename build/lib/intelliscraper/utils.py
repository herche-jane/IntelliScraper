import json
import re

from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_text(text):
    """ 移除文本中的空格和特殊字符 """
    return re.sub(r'\s+', '', text)

def element_to_string(element):
    """将元素转换为字符串表示"""
    return f"{element.name} {' '.join([f'{k}={v}' for k, v in element.attrs.items()])}"


def get_most_similar_element(current_html, target_json):
    rule_json = json.loads(target_json)
    paths = parse_rules_to_paths(rule_json)
    soup = BeautifulSoup(current_html, 'html.parser')
    all_elements_str = [element_to_string(el) for el in soup.find_all()]
    vectorizer = CountVectorizer().fit(all_elements_str)
    target_paths = get_most_similar_paths(current_html, paths, vectorizer)
    return target_paths



def get_most_similar_paths(html, paths, vectorizer):
    """根据层级路径构建特征向量，并直接找到对应的元素"""
    most_similar_paths = []
    for path in paths:
        most_similar_path = find_most_similar_element_path(html, path, vectorizer)
        if most_similar_path:
            most_similar_paths.append(most_similar_path)
    return most_similar_paths


def generate_element_path(element):
    """生成元素的完整路径"""
    path_parts = []
    while element and element.name:
        path_parts.append(element_to_string(element))
        element = element.parent
    return ' -> '.join(reversed(path_parts))



def find_most_similar_element_path(html, path, vectorizer):
    """在HTML中找到与给定路径最相似的元素路径"""
    soup = BeautifulSoup(html, 'html.parser')
    all_elements = soup.find_all()
    all_elements_paths = [generate_element_path(el) for el in all_elements]
    path_vector = vectorizer.transform([path])
    paths_vectors = vectorizer.transform(all_elements_paths)
    similarities = cosine_similarity(path_vector, paths_vectors)
    most_similar_index = similarities[0].argmax()
    return all_elements_paths[most_similar_index]

def parse_rules_to_paths(rules_json):
    """从JSON规则中提取层级路径"""
    paths = []
    for key, value in rules_json.items():
        paths.extend(value)
    return paths


def find_element_by_path(html, path):
    """根据路径找到HTML中的元素"""
    soup = BeautifulSoup(html, 'html.parser')
    current_element = soup

    for part in path.split(" -> "):
        if "[document]" in part:
            continue
        # 分割标签和属性
        match = re.match(r'(\w+)(.*)', part)
        tag = match.group(1) if match else ''
        attr_str = match.group(2).strip() if match else ''
        attrs = parse_attributes(attr_str)
        # 查找下一个元素
        found_element = current_element.find(tag, attrs)
        if found_element:
            current_element = found_element
    return current_element



def parse_attributes(attr_str):
    """解析标签的属性字符串"""
    attrs = {}
    attributes = split_attributes_improved(attr_str)
    for attribute in attributes:
        if '[' in attribute:  # 检查是否存在方括号内的列表
            # 使用正则表达式匹配键值对
            attr_pairs = re.findall(r'(\w+)=\[(.*?)\]|(\w+)=(\S+)', attr_str)
            for attr in attr_pairs:
                if attr[0]:  # 匹配到形如 key=[value1, value2] 的属性
                    key, value = attr[0], attr[1].split(',')
                    value = [v.strip(' "[]\'') for v in value]
                else:  # 匹配到形如 key=value 的属性
                    key, value = attr[2], attr[3]
                    value = value.strip(' "\'')
                attrs[key] = value
        else:
            # 没有列表的情况，直接按空格分割
            attrs_list = re.split(r'\s+', attribute.strip())
            for attr in attrs_list:
                if '=' in attr:
                    key, value = attr.split('=', 1)
                    value = value.strip(' "\'')
                    attrs[key] = value
    return attrs


def split_attributes_improved(attr_str):
    """
    Improved split function for attribute strings.
    This version supports attributes with hyphens and attributes within square brackets.
    It correctly splits attributes such as 'lang=zh data-server-rendered=true data-v-52866abc='.
    """
    # Regular expression to split by space while ignoring spaces inside square brackets and considering hyphens in attribute names
    pattern = r'(\w+(?:-\w+)*=[^\s\[]*(?:\[[^\]]*\])?)'
    attributes = re.findall(pattern, attr_str)
    return attributes

