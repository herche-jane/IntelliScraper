from setuptools import setup, find_packages

setup(
    name='IntelliScraper',
    version='1.0.2',
    packages=find_packages(),
    description='An advanced web scraping tool using BeautifulSoup and scikit-learn.',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/herche-jane/IntelliScraper',
    author='Herche Jane',
    author_email='524430556@qq.com',
    license='MIT',
    install_requires=[
        'beautifulsoup4',
        'scikit-learn',
        'requests',
        'utils'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
