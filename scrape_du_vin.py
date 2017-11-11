import lxml.html
from scrapelib import Scraper

class Vinny(Scraper):

    BASE_URL = 'https://vinchicago.com'

    def __init__(self, *args, **kwargs):
        self.requests_per_minute = 10
        super().__init__(*args, **kwargs)

    def newsletters(self):
        response = self.get(self.BASE_URL)
        page = lxml.html.fromstring(response.text)
        newsletter_links = page.xpath('//a[text()[contains(.,"Newsletter")]]')

        return {l.text: l.attrib['href'] for l in newsletter_links if '201' in l.text}

    def _wines_from_page(self, page):
        wines = []

        products = page.xpath('//div[@class="wdcproductinfo"]')
        for product in products:
            name_element, = product.xpath('h2/a')
            name = name_element.text

            description_element, = product.xpath('div[@class="wdcproductdesc"]')
            description = description_element.text.strip()

            scores = []

            reviews = product.xpath('div[@class="wdcproductreviews"]/div[@class="wdcproductreview"]')

            for review in reviews:
                score_element, = review.xpath('span[@class="wdcproductreviewscore"]')
                score = score_element.text.strip().rstrip('+')
                scores.append(score)

                try:
                    review_element, = review.xpath('span[@class="wdcproductreviewtext"]')
                except ValueError:
                    pass
                else:
                    review = review_element.text.strip()

            # Two "siblings" are just comments
            price_parent, = [s for s in product.itersiblings() if isinstance(s, lxml.html.HtmlElement)]

            try:
                price_element, = price_parent.xpath('div[@class="wdcbrowseproductprice"]/div[contains(@class, "product-price")]/div[contains(@class, "PricesalesPrice")]')
            except ValueError:
                price = 'Unlisted'
            else:
                price_dollars = price_element.find('span[@class="PricesalesPrice"]')
                price_cents = price_element.find('span[@class="supercents"]')
                price = '.'.join([price_dollars.text, price_cents.text])

            wines.append([name, description, scores, review, price])

        return wines


    def scrape(self):
        for newsletter, link in self.newsletters().items():
            response = self.get(self.BASE_URL + link, params={'limit': 100})
            assert response.status_code == 200

            page = lxml.html.fromstring(response.text)
            wines = self._wines_from_page(page)

            yield newsletter, wines


if __name__ == '__main__':

    import csv
    import sys

    vin = Vinny()

    writer = csv.writer(sys.stdout)
    writer.writerow(['newsletter', 'wine_name', 'vendor_description',
                     'score', 'review', 'price'])

    for newsletter, wines in vin.scrape():
        for wine in wines:
            writer.writerow([newsletter] + [attr for attr in wine])
