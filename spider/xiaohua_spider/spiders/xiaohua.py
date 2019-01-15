# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from spider.xiaohua_spider.items import XiaohuaSpiderItem


class XiaohuaSpider(scrapy.Spider):
    name = 'xiaohua'
    allowed_domains = ['xiaohuar.com']
    start_urls = ['http://www.xiaohuar.com/hua/']

    # 自定义头部 。 可以在下面代码中载入设置或写在settings.py中写
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
    }

    # 存放待爬取的url，scrapy会自动去重和重试失败链接，我们只需考虑往url集合中添加未爬取的url。
    url_set = set()

    def parse(self, response):
        """ 请求首页图集列表之后得到列表页，解析获得图集详情页地址 """
        # 首先重写parse，否则父类会报NotImplement异常
        # response.xpath() 。如果安装过lxml，scrapy默认用lxml.etree。etree.HTML(resp.content)
        a_list = Selector(response).xpath('//div[@class="img"]/a')
        for a in a_list:
            detail_url = a.xpath('.//@href').extract_first()
            if detail_url in self.url_set:
                # 已爬取过
                print('已经爬取过该页')
            else:
                # 添加到待爬取链接池
                self.url_set.add(detail_url)
                # 发现 画廊页url http://www.xiaohuar.com/s-1-2015.html ，和详情页http://www.xiaohuar.com/p-1-2015.html 路由存在规律，可以直接转换，节省一次requests请求和xpath解析。
                gallery_url = detail_url.replace('/p', '/s')
                # yield相当于同步函数里的返回值，callback相当于方法嵌套调用，只不过这两个关键字表现异步处理过程。yield生成请求对象（还没有发送请求）到队列中，框架从队列中取一个请求对象去请求，得到响应后再交给回调函数处理。
                yield Request(url=gallery_url, callback=self.img_parse)

        next_page = response.xpath('//*[@id="page"]/div/a[17]/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page,callback=self.parse)


    def img_parse(self, response):
        """ 解析请求画廊页后的html结果，生成item"""
        src_list = Selector(response).xpath('//div[@class="inner"]/a/img/@src').extract()       # ['https://xxxx.jpg', '']
        folder_name = Selector(response).xpath('//h1/text()').extract_first()

        for src in src_list:
            print('图片资源', src)      # self.log('图片资源', src)
            img_url = src
            # 由于网站开发技术历史原因，有路由形式访问的 '/d/file/20181216/small6ef7993ed1b6ce4f31d4b60f73c066571544975727.jpg'
            # 也有访问静态服务器接口形式的 'https://www.dxsabc.com/api/xiaohua/upload/min_img/20190110/20190110DMt7SdoZtk.jpg'
            if img_url.startswith('https'):
                pass
            else:
                # 路由形式的，协议http，没有解析xiaohuar.com
                img_url = 'http://www.xiaohuar.com' + img_url

            img_name = src.split('/')[-1]   # 20190110AdOgzcLVqR.jpg

            # item = XiaohuaSpiderItem(folder_name=folder_name, img_name=img_name, img_url=img_url)
            item = XiaohuaSpiderItem()
            item['folder_name'] = folder_name
            item['img_name'] = img_name
            item['img_url'] = img_url
            yield item


