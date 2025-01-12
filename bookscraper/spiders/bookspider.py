import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"

    #allowed_domains: only crawl website that is childern of this
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

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
        yield {
            'url' : response.url,
            'title' : response.css('.product_main h1::text').get(),
            'product_type' : all_table_rows[1].css('td::text').get(),
            'star_rating' : response.css('p.star-rating::attr(class)').get().replace('star-rating ', ''),
            'category' : response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
            'price' : response.css('.product_main p.price_color::text').get(),

        }

# to run spider: 'scrapy crawl bookspider' (name = bookspider)
# to run spider and save data in file:
    # scrapy crawl bookspider -o file_name.json/.csv/....

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