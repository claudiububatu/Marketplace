"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.id_producer = marketplace.register_producer()

    def run(self):
        products = self.products
        while True:
            product_index = 0
            while product_index < len(products):
                product = products[product_index]
                contor = 0
                published = False
                while contor < product[1] and not published:
                    if self.marketplace.publish(self.id_producer, product[0]):
                        time.sleep(product[2])
                        contor += 1
                    else:
                        time.sleep(self.republish_wait_time)
                    if contor == product[1]:
                        published = True
                if published:
                    product_index = product_index + 1
