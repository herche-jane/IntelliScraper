from intelliscraper.web_scraper import WebScraper

# wanted_list = ['北堂飘霜']
# scraper = WebScraper(wanted_list, url='https://blog.csdn.net/weixin_45487988?spm=1010.2135.3001.5343')
# results = scraper.build()
# for result in results:
#     print(result)
#
#
#
wanted_list = ['北堂飘霜']
scraper = WebScraper(wanted_list, url='https://blog.csdn.net/weixin_45487988?spm=1010.2135.3001.5343',max_reasult=100,similarity=0.6)
results = scraper.build()
for result in results:
    print(result)