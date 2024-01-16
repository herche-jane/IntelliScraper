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





def get_most_similar_paths(html, paths, vectorizer):
    """根据层级路径构建特征向量，并找到与之相似度大于或等于 0.5 的元素路径"""
    most_similar_paths = []
    soup = BeautifulSoup(html, 'html.parser')
    all_elements = soup.find_all()
    all_elements_paths = [generate_element_path(el) for el in all_elements]

    for path in paths:
        path_vector = vectorizer.transform([path])
        paths_vectors = vectorizer.transform(all_elements_paths)
        similarities = cosine_similarity(path_vector, paths_vectors)

        # 检查每个路径的相似度是否大于或等于 0.5
        for index, similarity in enumerate(similarities[0]):
            if similarity >= 0.7:
                most_similar_paths.append(all_elements_paths[index])
    return most_similar_paths

def get_most_similar_element(current_html, target_json):
    rule_json = json.loads(target_json)
    paths = parse_rules_to_paths(rule_json)
    soup = BeautifulSoup(current_html, 'html.parser')
    all_elements_str = [element_to_string(el) for el in soup.find_all()]
    vectorizer = CountVectorizer().fit(all_elements_str)
    target_paths = get_most_similar_paths(current_html,paths, vectorizer)
    if (len(target_paths) > 50):
        target_paths = target_paths[:50]
    return target_paths


def find_similar_elements(html, target_html, threshold=0.5):
    # 构建原始html特征向量
    html_elements_str, html_elements = build_feature_vector(html)
    # 构建目标html特征向量
    target_elements_str, _ = build_feature_vector(target_html)
    print(target_elements_str)
    vectorizer = CountVectorizer().fit(html_elements_str + target_elements_str)
    html_vec = vectorizer.transform(html_elements_str)
    target_vec = vectorizer.transform(target_elements_str)
    similarities = cosine_similarity(target_vec, html_vec)
    similar_elements = []
    for index, similarity in enumerate(similarities[0]):
        if similarity >= threshold:
            similar_elements.append(html_elements[index])
    return similar_elements


def build_feature_vector(html):
    """构建特征向量"""
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.findAll()
    elements_str = [element_to_string(el) for el in elements]
    return elements_str, elements

from bs4 import BeautifulSoup

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

