import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CeskaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.cnb.cz/system/modules/org.opencms.apollo/elements/list-ajax.jsp?contentpath=/cs/.content/lists/l_00014.xml&instanceId=li_793d48a5&elementId=le_3f676017&sitepath=/cs/cnb-news/aktuality/&subsite=/sites/cnb/cs/&__locale=cs&loc=cs&option=append&hideOptions=true&reloaded&sort=priority_d&page={}'
class CeskaSpider(scrapy.Spider):
	name = 'ceska'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		articles = response.xpath('//div[@class="teaser "]')
		for article in articles:
			date = ''.join(article.xpath('.//div[@class="date"]/text()').get().split())
			post_links = article.xpath('.//h2/a/@href').get()
			try:
				if not 'pdf' in post_links:
					yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))
			except TypeError:
					print("Article not available")
		if response.xpath('//h2/a').get():
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)


	def parse_post(self, response, date):

		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="text"]//text() | //div[@class="block news"]/div/p//text() | //main//div[@class="ap-section "]//text()[not (ancestor::div[@class="ap-panel panel-group"])] | //table//text() | //div//em//text()|//div[@class="boarddecision-record"]/div//following-sibling::p|//div[@class="block vlog"]/div//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CeskaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
