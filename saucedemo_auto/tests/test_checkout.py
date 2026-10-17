# -*- coding: utf-8 -*-
"""结算模块用例：CHECKOUT-01 ~ CHECKOUT-08。"""
import pytest

from config import FIRST_NAME, LAST_NAME, POSTAL_CODE
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage


@pytest.fixture()
def cart_with_two_items(logged_in):
    """前置：登录并添加 2 个商品。"""
    page = InventoryPage(logged_in)
    page.add_to_cart("Sauce Labs Backpack")
    page.add_to_cart("Sauce Labs Bike Light")
    return page.open_cart()


class TestCheckout:
    def test_full_checkout(self, cart_with_two_items):
        """CHECKOUT-01 正常完成结算全流程"""
        checkout = cart_with_two_items.checkout()
        checkout.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
        checkout.finish()
        assert checkout.get_complete_message() == "Thank you for your order!", \
            "下单成功应显示感谢信息"

    def test_blank_first_name(self, cart_with_two_items):
        """CHECKOUT-02 名字为空校验"""
        checkout = cart_with_two_items.checkout()
        checkout.fill_info("", LAST_NAME, POSTAL_CODE)
        assert "First Name is required" in checkout.get_error()

    def test_blank_last_name(self, cart_with_two_items):
        """CHECKOUT-03 姓氏为空校验"""
        checkout = cart_with_two_items.checkout()
        checkout.fill_info(FIRST_NAME, "", POSTAL_CODE)
        assert "Last Name is required" in checkout.get_error()

    def test_blank_postal_code(self, cart_with_two_items):
        """CHECKOUT-04 邮编为空校验"""
        checkout = cart_with_two_items.checkout()
        checkout.fill_info(FIRST_NAME, LAST_NAME, "")
        assert "Postal Code is required" in checkout.get_error()

    def test_total_calculation(self, cart_with_two_items):
        """CHECKOUT-05 结算总额计算正确：Total = Item total + Tax"""
        checkout = cart_with_two_items.checkout()
        checkout.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
        total = checkout.get_total()
        assert total == pytest.approx(checkout.get_item_total() + checkout.get_tax(), abs=0.01), \
            f"Total({total}) 应等于 Item total + Tax"

    def test_overview_item_count(self, cart_with_two_items):
        """CHECKOUT-06 概览页商品数量正确"""
        checkout = cart_with_two_items.checkout()
        checkout.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
        assert checkout.get_item_count() == 2, "概览页应显示 2 个商品"

    def test_cancel_checkout(self, cart_with_two_items):
        """CHECKOUT-07 结算信息页可取消"""
        cart = cart_with_two_items
        checkout = cart.checkout()
        checkout.cancel()
        assert checkout.is_visible(*cart.CHECKOUT_BTN), "取消后应返回购物车页"

    def test_cart_cleared_after_order(self, cart_with_two_items):
        """CHECKOUT-08 完成订单后购物车清空"""
        checkout = cart_with_two_items.checkout()
        checkout.fill_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
        checkout.finish()
        assert checkout.get_complete_message() == "Thank you for your order!"
        # 返回商品列表，购物车角标应消失（数量为 0）
        inventory = InventoryPage(checkout.driver)
        assert inventory.get_cart_badge() == 0, "下单后购物车应清空"
