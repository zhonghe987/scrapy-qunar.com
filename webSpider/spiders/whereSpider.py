#coding:utf8

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
import scrapy
from webSpider.items import WebspiderItem
from scrapy.spider import BaseSpider 
from scrapy.selector import Selector
from scrapy.http import Request
import  json
import  urlparse



class whereSpider(CrawlSpider):
    name = "where"
    allowed_domains = ['qunar.com']
    start_urls = ["http://piao.qunar.com/ticket/list.json?keyword=上海&from=mps_remdd&page=1"]
    
    #rule = [ Rule(LinkExtractor(allow=('.json', )), callback='parse'),
     #        Rule(LinkExtractor(allow=('.html', )), callback='inner_page'),
      #      ]
    
    #http://piao.qunar.com/ticket/list.json?keyword=上海&from=mps_remdd&total=790&page=1
    #def start_requests(self):
    #    yield Request(url =u"http://piao.qunar.com/ticket/list.json?keyword=上海&from=mps_remdd&page=1",callback = self.barse )
        
        

    def parse(self,response):
        urls = urlparse.urlsplit(response.url)
        num =  int(urls.query.split('=')[-1]) + 1
        query = u'keyword=上海&from=mps_remdd&page=%s'%num       
        parse = '://'.join(urls[0:2])
        site = json.loads(response.body)
        item = WebspiderItem()
        if site['ret']:
            title = []
            price = []
            logo_url = []
            addressPoint = []
            saleCount = []
            for k in site['data']['sightList']:
                title.append( k["sightName"])
                price.append( k["qunarPrice"])
                logo_url.append(k["sightImgURL"])
                addressPoint.append(k['point'])
                saleCount.append(k['saleCount'])
                fllow_url = urlparse.urljoin(parse,'ticket/detail_%s.html#from=mps_remdd'%k["sightId"])
                yield Request(url = fllow_url, callback = self.inner_page)
            item['title'] = title
            item['logo_url'] = logo_url
            item['price'] = price
            item['addressPoint']  = addressPoint
            item['saleCount'] = saleCount
            
            yield Request(url = '?'.join([urlparse.urljoin(parse,urls[2]),query]),callback = self.parse)
            yield item
          
        
    def inner_page(self,response):
        res = Selector(response)
        item = WebspiderItem()
        if not res.xpath('//h1[@class="sight_info_name"]/@title'):
            yield Request(url=response.url, dont_filter=True)
        item['detil_title'] = res.xpath('//h1[@class="sight_info_name"]/@title').extract()[0]
        title_ticket = res.xpath('//h3[@class="ticket_item_title ticket_item_title_mainpage"]/text()').extract()
            
        price = res.xpath('//em[@class="txt_orange"]/strong[not(@style)]/text()').extract()
        if title_ticket and price:
            item['ticket_title'] = ','.join(['--'.join(k) for k in zip(title_ticket,price)])
        else:
            item['ticket_title'] = ''
        item['introduce'] = ''.join(res.xpath('//div[@class="intro_item_des"]/div[@class="module_des_content"]/p/text()').extract())
        yield item
        