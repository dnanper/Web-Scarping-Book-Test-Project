import random

import scrapy
from bookscraper.items import BookItem

# First to know: Yield is like Return, but it generates new Object and Pause the current code_block
# After finish the code_block call by Yield, compyler continues run the previous code_block
# Like BL in Kien Truc May Tinh

##### PROXY
# Unlike browser headers, ID is identical address for each computer. This ID is for computer to gain back the
# information having requested from website
# So that, even though we change browser headers each time request, the ADMIN WEBSITE can block us using
# ID (Cause each computer only has one ID)
# => to prevent that case, use ROTATING PROXY:
    # Use ID from Free Proxy List, which contains many ID from big City so almost Websites ignore those ID
        # Very Low, beacause they are free so many people use them -> Not Good
        # May not work
        # Must to change oftenly
        # Use middleware and pip install some libraries
    # Smart Proxy: Paid (Money)
    # Proxy API: ScrapeOps
        # Paid
        # Don't even need Browser Header /User-Agent anymore

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"

    #allowed_domains: only crawl website that is childern of this
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    # Can modify default in here instead of in settings file
    custom_settings = {
        'FEEDS': {
            'book_data.json': {
                'format': 'json',
                'overwrite': True
            }
        }
    }

    ### USER-AGENT / BROWSER HEADERS
    # Create list of User-agent and rotately using each of it in order to avoid ban from website
    # Or we can use a middlewares contains thousands of fake user id, instead of 5. This call API
    # user_agent_list = [
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
    # ]

    # this function automatically run first
    # the response for function PARSE is start_urls
    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            # to see detail of a book
            # get link (URL)
            detail_page = book.css('h3 a::attr(href)').get()
            if 'catalogue/' in detail_page:
                detail_page_url = 'https://books.toscrape.com/' + detail_page
            else:
                detail_page_url = 'https://books.toscrape.com/catalogue/' + detail_page
            # this is not recursion, just a function call part:
            #   call the parse_book_detail function again for each book
            yield response.follow(detail_page_url, callback=self.parse_book_detail)
            # above(headers): randomly use different user-agent

            # yield {
            #     'name' : book.css('h3 a::text').get(),
            #     'price' : book.css('div.product_price p.price_color::text').get(),
            #     'URL' : book.css('h3 a').attrib['href']
            # }

        #to move to continue page to crawl data
        next_page = response.css('li.next a').attrib['href'] #contain the URL of next page
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

            #recursion part
            yield response.follow(next_page_url, callback=self.parse)
    # parse book detail function
    # now this function only work in the book detail page
    # the response for PARSE_BOOK_DETAIL is detail_page_url
    def parse_book_detail(self, response):
        all_table_rows = response.css('table tr')
        book_item = BookItem()
        # Here we can use a CLASS to store all this information: book object
        book_item['url'] = response.url,
        book_item['title'] = response.css('.product_main h1::text').get(),
        book_item['upc'] = all_table_rows[0].css("td ::text").get()
        book_item['product_type'] = all_table_rows[1].css("td ::text").get(),
        book_item['price_excl_tax'] = all_table_rows[2].css("td ::text").get(),
        book_item['price_incl_tax'] = all_table_rows[3].css("td ::text").get(),
        book_item['tax'] = all_table_rows[4].css("td ::text").get(),
        book_item['availability'] = all_table_rows[5].css("td ::text").get(),
        book_item['num_reviews'] = all_table_rows[6].css("td ::text").get(),
        book_item['stars'] = response.css("p.star-rating").attrib['class'],
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
        book_item['price'] = response.css('p.price_color ::text').get(),

        yield book_item

# to run spider: 'scrapy crawl bookspider' (name = bookspider)
# to run spider and save data in file:
    # scrapy crawl bookspider -o file_name.json/.csv/....

# if already set default: FEED in settings, then use: scrapy crawl bookspider

### we can practice (test) with the HTML with ipython with:
#           SCRAPY SHELL.
# INSIDE SHELL:
# fetch url of website to shell, so we can access the data of that HTML
# response: get the information we want: type_tag.class_name

# filter step:
    # to get the content (text) of a tag, write: tag1 tag2 tag3
        # example: book.css('h3 a::text').get()
        # where book is a article

        # example2 : get price of a book:
        # book.css('div.product_price p.price_color::text').get()
        # format: type_tag.class_name

    # to get the data of attribute from tag, write: .attrib['name_of_attribute']
        #example: to get URL from href -> book.css('h3 a').attrib['href']
            # href is an attribute of tag 'a'

    # if the tag that we want to get data doesn't have ID/CLASS -> we can't use CSS to get data
    # instead, we use XPATH: if we know an ID/CLASS tag near it, we can use that tag as a mock
        # example:
    # response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        # get to tag<ul class = breadcrumb> -> <li class = active> -> get the previous tag of that <li> tag
        # using "preceding-sibling" -> get to <a> -> text()


# to exit shell: EXIT.