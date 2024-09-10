#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Semaphore
import time

import unittest

import logging
from logging.handlers import RotatingFileHandler

LOGGER = logging.getLogger('my_logger')
LOGGER.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
HANDLER = RotatingFileHandler("marketplace.log", maxBytes=1024 * 512, backupCount=20)
HANDLER.setFormatter(FORMATTER)
FORMATTER.converter = time.gmtime
LOGGER.addHandler(HANDLER)

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    producer_and_his_list_of_products = {}
    product_and_its_producer = {}
    carts = {}
    register_sem = Semaphore(value=1)
    max_elem_sem = Semaphore(value=1)
    cart_size_sem = Semaphore(value=1)
    rmv_from_cart_sem = Semaphore(value=1)

    def __init__(self, queue_size_per_producer):
        """
        Constructor
        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.cart_id = 0
        self.next_cart_id = 1
        self.producer_id = 0
        self.next_producer_id = 1

        LOGGER.info('Initialized all the elements that \
                    are needed for the implementation of the homework!')

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        # I keep track of the current id and next id of our producers
        current_producer_id = self.producer_id
        LOGGER.info("Trying to register the producer with the id %d..", current_producer_id)
        self.producer_and_his_list_of_products[current_producer_id] = []
        self.register_sem.acquire()
        self.producer_id = self.next_producer_id
        self.register_sem.release()
        self.next_producer_id = self.next_producer_id + 1

        LOGGER.info('Producer with the id %d registered succesfully!', current_producer_id)

        return current_producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        # using semaphore to be thread safe
        self.max_elem_sem.acquire()
        LOGGER.info('Trying to publish the product %s on the marketplace..', product)

        # get correctly the lengths
        queue_size = self.queue_size_per_producer
        nr_of_products = len(self.producer_and_his_list_of_products[int(producer_id)])
        if nr_of_products < queue_size:
            self.producer_and_his_list_of_products[int(producer_id)].append(product)
            self.product_and_its_producer[product] = int(producer_id)
            LOGGER.info('Published the product for producer %d successfully!', producer_id)
            self.max_elem_sem.release()
            return True
        LOGGER.info('Failed to publish the product!')
        self.max_elem_sem.release()
        return False


    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        self.cart_size_sem.acquire()

        LOGGER.info("Trying to create a cart with the id %d", self.cart_id)

        self.carts[self.cart_id] = []
        self.cart_id = self.next_cart_id
        self.next_cart_id = self.next_cart_id + 1

        LOGGER.info("Created a new cart with the id %d!", self.cart_id - 1)

        self.cart_size_sem.release()
        return self.cart_id - 1

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        LOGGER.info('Trying to add the product %s to cart %d', product, cart_id)

        for producer in self.producer_and_his_list_of_products:
            # I get the list of products that a producer has
            products = self.producer_and_his_list_of_products[producer]
            counter = 0

            for prod in products:
                if product == prod:
                    counter = counter + 1
            # if the product is already created by producer
            if counter > 0:
                # put it in the cart and remove from product's list
                self.carts[cart_id].append(product)
                self.producer_and_his_list_of_products[producer].remove(product)
                LOGGER.info('A new product was added to the cart successfully!')
                return True
        LOGGER.info('Failed to add a new product!')
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        # taking producer using our dictionary
        LOGGER.info('Trying to remove product %s from the cart %d', product, cart_id)
        producer = self.product_and_its_producer[product]
        self.rmv_from_cart_sem.acquire()

        self.carts[cart_id].remove(product)
        self.producer_and_his_list_of_products[producer].append(product)

        LOGGER.info(
            'Removed %s from the cart_id %s successfully!',
            product, cart_id)

        self.rmv_from_cart_sem.release()

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        # take the information from cart and remove the cart from dictionary
        if cart_id in self.carts:
            final_order = self.carts[cart_id]
            del self.carts[cart_id]
            LOGGER.info("Placed the order successfully!")
            return final_order
        return None


class TestMarketplace(unittest.TestCase):
    """Class that tests the whole process created by Marketplace"""
    def setUp(self):
        """Initialization of the marketplace"""
        self.marketplace_dimension = 3
        self.size = 10

        self.marketplace = Marketplace(self.marketplace_dimension)

    def test_register_producer(self):
        """Test function which tests if register_producer runs correctly"""
        i = 0
        while i < self.size:
            producer_id = self.marketplace.register_producer()
            self.assertEqual(producer_id, i, True)
            i = i + 1

    def test_publish(self):
        """Test function which tests if publish runs correctly"""

        product1 = str({
            "product_type": "Coffee",
            "name": "Japan",
            "acidity": 3.75,
            "roast_level": "HIGH",
            "price": 3
        })

        product2 = str({
            "product_type": "Tea",
            "name": "Linden",
            "type": "Herbal",
            "price": 9
        })

        producer1 = self.marketplace.register_producer()
        self.marketplace.publish(producer1, product1)
        self.marketplace.publish(producer1, product2)

        result1 = [product1, product2]
        real_result1 = self.marketplace.producer_and_his_list_of_products[producer1]

        self.assertEqual(real_result1, result1, False)

        producer2 = self.marketplace.register_producer()
        self.marketplace.publish(producer2, product1)

        result2 = [product1]
        real_result2 = self.marketplace.producer_and_his_list_of_products[producer2]

        self.assertEqual(real_result2, result2, False)

    def test_new_cart(self):
        """Test function which tests if new_cart runs correctly"""

        i = 0
        while i < self.size:
            cart_id = self.marketplace.new_cart()
            self.assertEqual(cart_id, i, False)
            i = i + 1

    def test_add_to_cart(self):
        """Test function which tests if add_to_cart runs correctly"""

        product1 = str({
            "product_type": "Coffee",
            "name": "Japan",
            "acidity": 3.75,
            "roast_level": "HIGH",
            "price": 3
        })

        product2 = str({
            "product_type": "Tea",
            "name": "Linden",
            "type": "Herbal",
            "price": 9
        })

        producer1 = self.marketplace.register_producer()
        cart1 = self.marketplace.new_cart()

        producer2 = self.marketplace.register_producer()
        cart2 = self.marketplace.new_cart()

        self.marketplace.publish(producer1, product1)
        self.marketplace.publish(producer1, product2)

        self.marketplace.add_to_cart(cart1, product1)
        self.marketplace.add_to_cart(cart1, product2)

        self.marketplace.publish(producer2, product2)
        self.marketplace.add_to_cart(cart2, product2)

        test_carts1 = [product1, product2]
        real_carts1 = self.marketplace.carts[cart1]
        self.assertEqual(real_carts1, test_carts1, True)

        test_carts2 = [product2]
        real_carts2 = self.marketplace.carts[cart2]

        self.assertEqual(real_carts2, test_carts2, True)


    def test_remove_from_cart(self):
        """Test function which tests if remove_from_cart runs correctly"""

        product1 = str({
            "product_type": "Coffee",
            "name": "Japan",
            "acidity": 3.75,
            "roast_level": "HIGH",
            "price": 3
        })

        product2 = str({
            "product_type": "Tea",
            "name": "Linden",
            "type": "Herbal",
            "price": 9
        })

        producer = self.marketplace.register_producer()
        cart = self.marketplace.new_cart()

        self.marketplace.publish(producer, product1)
        self.marketplace.publish(producer, product2)

        self.marketplace.add_to_cart(cart, product1)
        self.marketplace.add_to_cart(cart, product2)

        self.marketplace.remove_from_cart(cart, product1)
        test_carts = [product2]
        real_carts = self.marketplace.carts[cart]
        self.assertEqual(real_carts, test_carts, True)

    def test_place_order(self):
        """Test function which tests if place_order runs correctly"""

        product1 = str({
            "product_type": "Coffee",
            "name": "Japan",
            "acidity": 3.75,
            "roast_level": "HIGH",
            "price": 3
        })

        product2 = str({
            "product_type": "Tea",
            "name": "Linden",
            "type": "Herbal",
            "price": 9
        })

        producer = self.marketplace.register_producer()
        cart = self.marketplace.new_cart()

        self.marketplace.publish(producer, product1)
        self.marketplace.publish(producer, product2)

        self.marketplace.add_to_cart(cart, product1)
        self.marketplace.add_to_cart(cart, product2)

        real_order = self.marketplace.carts[cart]
        order = self.marketplace.place_order(cart)

        self.assertEqual(order, real_order, True)
