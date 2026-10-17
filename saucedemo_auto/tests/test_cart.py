# -*- coding: utf-8 -*-
"""购物车模块用例：CART-01 ~ CART-05。"""
from pages.inventory_page import InventoryPage


class TestCart:
    PRODUCT_A = "Sauce Labs Backpack"
    PRODUCT_B = "Sauce Labs Bike Light"
    PRODUCT_C = "Sauce Labs Bolt T-Shirt"

    def test_add_single_item(self, logged_in):
        """CART-01 添加单个商品到购物车"""
        page = InventoryPage(logged_in)
        page.add_to_cart(self.PRODUCT_A)
        assert page.is_added(self.PRODUCT_A), "添加后按钮应变为 Remove"
        assert page.get_cart_badge() == 1, "购物车角标应显示 1"

    def test_add_multiple_items(self, logged_in):
        """CART-02 添加多个商品数量累加"""
        page = InventoryPage(logged_in)
        for name in (self.PRODUCT_A, self.PRODUCT_B, self.PRODUCT_C):
            page.add_to_cart(name)
        assert page.get_cart_badge() == 3, "添加 3 个商品后角标应显示 3"

    def test_remove_item(self, logged_in):
        """CART-03 从购物车移除商品"""
        page = InventoryPage(logged_in)
        page.add_to_cart(self.PRODUCT_A)
        page.add_to_cart(self.PRODUCT_B)
        page.remove_from_cart(self.PRODUCT_A)
        assert page.get_cart_badge() == 1, "移除 1 个后角标应减为 1"
        cart = page.open_cart()
        assert cart.get_item_count() == 1, "购物车应只剩 1 个商品"
        assert cart.get_item_names() == [self.PRODUCT_B]

    def test_cart_page_info(self, logged_in):
        """CART-04 购物车页面展示商品信息"""
        page = InventoryPage(logged_in)
        page.add_to_cart(self.PRODUCT_A)
        cart = page.open_cart()
        assert cart.get_item_count() == 1
        assert self.PRODUCT_A in cart.get_item_names(), "购物车应包含已添加商品"

    def test_empty_cart(self, logged_in):
        """CART-05 空购物车正常打开"""
        cart = InventoryPage(logged_in).open_cart()
        assert cart.is_empty(), "未添加商品时购物车应为空"
        assert cart.get_item_names() == [], "空购物车不应列出任何商品"
