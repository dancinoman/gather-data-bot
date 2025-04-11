
from bs4 import BeautifulSoup
import time
import re
#TODO fix the errors within Scrape class

class Scrape:

    def __init__(self):
        self.restaurants = []
        self.detailed_restaurants = []
        self.rating_restaurants = []
        self.comments = []
        self.customer_rating = []
        self.customer_comment = []
        self.customer_rating_date = []

    def individual_content(self, page_source, id_key):
        """
        Scrapes individual restaurant pages.
        """

        # Get page soup
        detailed_soup = BeautifulSoup(page_source, 'html.parser')

        average_price = detailed_soup.find('div', class_='restaurant-price').get('data-tooltip')
        address = detailed_soup.find('span', class_='street-address').text.strip()
        description = detailed_soup.find('div', class_='aboutus-text').text.strip()

        amount_of_picture  = detailed_soup.find('a','btn-e thick bold black rounded mb10 mt30 block')

        # Filter empty value
        if amount_of_picture is not None:
            amount_of_picture = re.findall('\d', amount_of_picture.text)
        else:
            amount_of_picture = ["0"]

        # Get features list
        features_group = detailed_soup.find('div', "row mt5 mb5", False)


        if features_group is not None:
            features_group.find_all('span', class_='action-btn-group')
            features = [element.text.strip() for element in features_group if element]
        else:
            features = []

        #################### RATINGS ####################
        average_rating = detailed_soup.find('span', 'google_rating_bold')
        if average_rating is not None: average_rating = average_rating.text.strip()
        else: average_rating = None

        amount_of_rating = detailed_soup.find('a', class_='reviewscard_rating')

        if amount_of_rating is not None:
            amount_of_rating = amount_of_rating.text.strip()
            amount_of_rating = re.findall('\d', amount_of_rating)
            amount_of_rating = ''.join(amount_of_rating)
        else:
            amount_of_rating = None
        #################### COMMENTS ###################

        # Check for at least one comment exist
        customer_rating_test = detailed_soup.find('span', 'icon-box wider ratings border-good icon-dark icon-circle text-thick')
        if customer_rating_test is not None:
            customer_ratings = detailed_soup.find_all('div', class_='pull-right')
            for rating in customer_ratings[:-1]:
                if rating.find('span') is not None:
                    self.customer_rating.append(rating.find('span').text.strip())

            customer_comments = detailed_soup.find_all('p', class_='mt20 mb20 reviews-desc')
            customer_rating_dates = detailed_soup.find_all('span', class_='review-date')

            self.customer_comment = [element.text.strip() for element in customer_comments if element]
            self.customer_rating_date = [element.text.strip() for element in customer_rating_dates if element]
            

        self.detailed_restaurants.append(
            {
                "id_resto": id_key,
                "amount_pictures": "".join(amount_of_picture),
                "address": address,
                "average_price": average_price,
                "features": ",".join(features),
                "description" : description
            }
        )

        self.rating_restaurants.append(
            {
                "id_resto": id_key,
                "average_rating": average_rating,
                'amount_of_rating': amount_of_rating
            }
        )

        for i in range(len(self.customer_rating)):
            self.comments.append(
                {
                    "id_resto": id_key,
                    "customer_rating": self.customer_rating[i],
                    "customer_comment": self.customer_comment[i],
                    "customer_rating_date": self.customer_rating_date[i]
                }
            )

        return self.detailed_restaurants, self.rating_restaurants, self.comments
