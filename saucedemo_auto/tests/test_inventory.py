# -*- coding: utf-8 -*-
"""商品列表模块用例：INV-01 ~ INV-05。"""
from pages.inventory_page import InventoryPage


class TestInventory:
    def test_default_six_items(self, logged_in):
        """INV-01 商品列表默认展示 6 个商品"""
        page = InventoryPage(logged_in)
        assert page.get_item_count() == 6, f"默认应展示 6 个商品，实际 {page.get_item_count()} 个"

    def test_sort_price_low_to_high(self, logged_in):
        """INV-02 按价格从低到高排序"""
        page = InventoryPage(logged_in)
        page.sort_by("lohi")
        prices = page.get_prices()
        assert prices == sorted(prices), f"价格应升序，实际 {prices}"

    def test_sort_price_high_to_low(self, logged_in):
        """INV-03 按价格从高到低排序"""
        page = InventoryPage(logged_in)
        page.sort_by("hilo")
        prices = page.get_prices()
        assert prices == sorted(prices, reverse=True), f"价格应降序，实际 {prices}"

    def test_open_product_detail(self, logged_in):
        """INV-05 点击商品名称进入详情页"""
        page = InventoryPage(logged_in)
        page.open_product("Sauce Labs Backpack")
        assert "/inventory-item.html" in logged_in.current_url, \
            f"应进入商品详情页，实际 URL: {logged_in.current_url}"
