import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"

    #allowed_domains: only crawl website that is childern of this
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            yield {
                'name' : book.css('h3 a::text').get(),
                'price' : book.css('div.product_price p.price_color::text').get(),
                'URL' : book.css('h3 a').attrib['href']
            }

        #to move to continue page to crawl data
        next_page = response.css('li.next a').attrib['href'] #contain the URL of next page
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

            #recursion part
            yield response.follow(next_page_url, callback=self.parse)

# to run spider: 'scrapy crawl bookspider'

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

# to exit shell: EXIT.
