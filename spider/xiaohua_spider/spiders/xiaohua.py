# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from xiaohua_spider.items import XiaohuaSpiderItem

class XiaohuaSpider(scrapy.Spider):
    name = 'xiaohua'
    allowed_domains = ['xiaohuar.com']
    start_urls = ['http://www.xiaohuar.com/hua/']

    customer_settings={
        'DEFAULT_REQUEST_HEADERS':{
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    }
    # 存放待爬取的url,scrapy会自动去重和重试失败连接,我们只需考虑往url集合中添加未爬取的url
    url_set = set()

    def parse(self, response):
        """
        请求首页图集列表之后得到列表页,解析获得图集详情页地址
        首先重写parse,否责父类会报NotImplement异常

        """
        # response.xpath()如果安装过lxml,scrapy默认用lxml.etree.
        # etree.html(resp.content)
        a_list = Selector(response).xpath('//div[@class="img"]/a')
        for a in a_list:
            detail_url=a.xpath('./@href').extract_first()
            if detail_url in self.url_set:
                pass
            else:
                # 添加到待爬取连接池
                self.url_set.add(detail_url)
                # 发现 画廊页url http://www.xiaohuar.com/s-1-2015.html,和详情页http://www.xiaohuar.com/p-1-2015.html 路由存在规律,可以直接转换,节省一次request请求和xpath解析.
                galler_url = detail_url.replace('/p','/s')
                # requests.get(galler_url)
                # yield相当于同步函数里的返回值,callback相当于方法嵌套调用,只不过这两个关键字表现异步处理过程,yield生成请求对象(还没有发送请求)到队列中,框架从队列中取出一个请求对象去请求,得到响应后再交给回调函数处理.
                # https: // www.dxsabc.com / api / xiaohua / upload / min_img / 20190110 / 20190110AdOgzcLVqR.jpg
                yield Request(url=galler_url,callback=self.img_parse)


    def img_parse(self,response):
        # 解析请求画廊页后的html结果,生成item
        # //h1/text()
        src_list = Selector(response).xpath('//div[@class="inner"]/a/img/@src').extract()  #['']
        folder_name = Selector(response).xpath('//h1/text()').extract_first()


        for src in src_list:
            print('图片资源',src)       # self.log('图片资源',src)

            img_url = src
            if src[:2] == '/d':
                img_url = 'http://www.xiaohuar.com'+src
            else:
                pass
            img_name = src.split('/')[-1]
            # http: // www.xiaohuar.com
            # item = XiaohuaSpiderItem(folder_name=folder_name,img_name=img_name...)
            item = XiaohuaSpiderItem()
            item['folder_name'] = folder_name
            item['img_url'] = img_url
            item['img_name'] = img_name
            yield item