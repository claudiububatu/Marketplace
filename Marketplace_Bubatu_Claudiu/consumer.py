"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import time
from threading import Thread
import sys

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs.get("name")

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()

            for operation in cart:
                quantity = operation["quantity"]
                my_type = operation["type"]
                product = operation["product"]
                if my_type == "add":
                    for _ in range(quantity):
                        while not self.marketplace.add_to_cart(cart_id, product):
                            time.sleep(self.retry_wait_time)
                elif my_type == "remove":
                    for _ in range(quantity):
                        self.marketplace.remove_from_cart(cart_id, product)

            placed_order = self.marketplace.place_order(cart_id)
            contor = 0
            while contor < len(placed_order):
                purchased_order = placed_order[contor]
                # flush necessary to get rid of junk data
                sys.stdout.flush()
                print(f"{self.name} bought {purchased_order}")
                contor = contor + 1
                