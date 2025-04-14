
from bs4 import BeautifulSoup
import time
import re
#TODO fix the errors within Scrape class

class Scrape:
    def __init__(self):

        self.restaurants = []
        self.detailed_restaurants = []
        self.comments = []


    def cover_content(self, resto, id):
        # From main Div
        lat = resto.get('data-lat')
        lon = resto.get('data-lon')

        # From link
        link = resto.find_all('a')
        resto_link = link[2]
        unique_page = resto_link.get('href')
        raw_name = resto_link.text.split()
        name = " ".join(raw_name)

        # From hash tag
        hash_div = resto.find('div', class_='color-gray mb5 lh-normal search-cuisine-box')
        # Skip if there is no hash tag
        if hash_div != None:
            hash_elements = hash_div.find_all('a')

            hash_tags = []
            for hash in hash_elements:
                hash_tags.append(hash.text.strip())
        self.restaurants.append(
            {
                "id": id,
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "hash_tags": ",".join(hash_tags),
                "unique_page": unique_page
            }
        )

        return unique_page

    def individual_content(self, page_source, id):
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

        #################### COMMENTS ###################

        # Check for at least one comment exist
        customer_rating = detailed_soup.findAll('div', 'reviews-card mb20')

        self.detailed_restaurants.append(
            {
                "id": id,
                "amount_pictures": "".join(amount_of_picture),
                "address": address,
                "average_price": average_price,
                "features": ",".join(features),
                "description" : description
            }
        )

        for cus_rating in customer_rating:
            self.comments.append({
                "id": id,
                "rating": cus_rating.find("div", "pull-right").find("span").text.strip(),

                "text": cus_rating.find("p", "mt20 mb20 reviews-desc").text.strip(),
                "date": cus_rating.find("span", "review-date").text.strip(),
                "average_rating": average_rating,
                'amount_of_rating': amount_of_rating
            })

        return self.restaurants, self.detailed_restaurants, self.comments
