# Define your item pipelines here
# Prettify the data
# Also able to store data instead of file .json/ .csv

# Pipelines between Yield and Item

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:

    # This function is automatically called create an item
    def process_item(self, item, spider):
        # ItemAdapter: return the object that contains all attributes of an unknown class Object(item)
        # adapter is like a map, with (key, value) = (attribute, value)
        adapter = ItemAdapter(item)

        # Get all the name of attribute of an Object
        # Get key
        field_names = adapter.field_names()

        # Delete all space between words in string, except 'description'
        for field_name in field_names:
            if field_name != 'description':
                # Get the value of that attribute
                value = adapter.get(field_name)
                # Assign the value after delete all space
                adapter[field_name] = value[0].strip()

        # Covert all to lowercase: For 'category' and 'product_type'
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        # Price + Tax: convert string to float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        # Availability: from 'In stock (19 available)' -> (int)19
        availability_string = adapter.get('availability')
        split_string_arr = availability_string.split('(')
        if len(split_string_arr) < 2:
            adapter['availability'] = 0
        else:
            adapter['availability'] = int(split_string_arr[1].split(' ')[0])

        # Review: Convert String to Int
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)

        # Star_rating: convert text to Int
        stars_string = adapter.get('stars')
        stars_text_value = stars_string.split(' ')[1].lower()
        if stars_text_value == "zero":
            adapter['stars'] = 0
        elif stars_text_value == "one":
            adapter['stars'] = 1
        elif stars_text_value == "two":
            adapter['stars'] = 2
        elif stars_text_value == "three":
            adapter['stars'] = 3
        elif stars_text_value == "four":
            adapter['stars'] = 4
        elif stars_text_value == "five":
            adapter['stars'] = 5

        return item
