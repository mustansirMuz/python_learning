from datetime import datetime
from typing import List


class MenuItem:
    def __init__(self, name: str, price: float) -> None:
        self.name: str = name
        self.price: float = price


class Customer:
    def __init__(self, name: str) -> None:
        self.name: str = name


class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int) -> None:
        self.menu_item: MenuItem = menu_item
        self.quantity: int = quantity


class Order:
    def __init__(self, customer: Customer, items: List[OrderItem]) -> None:
        self.customer: Customer = customer
        self.order_items: List[OrderItem] = items


class Reservation:
    def __init__(
        self, customer: Customer, reservation_time: datetime, no_of_people: int
    ) -> None:
        self.customer: Customer = customer
        self.reservation_time: datetime = reservation_time
        self.no_of_people: int = no_of_people


class Restaurant:
    def __init__(self) -> None:
        self.menu_items: List[MenuItem] = []
        self.table_reservations: List[Reservation] = []
        self.customer_orders: List[Order] = []

    def add_item_to_menu(self, item: MenuItem) -> None:
        """
        Adds an item to the menu
        """
        self.menu_items.append(item)

    def display_menu(self) -> None:
        """
        Displays the menu in a human-readable format
        """
        print("Menu Item\tPrice")
        for menu_item in self.menu_items:
            print(f"{menu_item.name}\t\tRs. {menu_item.price}")

    def book_reservation(self, reservation: Reservation) -> None:
        """
        Creates a reservation for the given customer, time and no_of_people
        """
        self.table_reservations.append(reservation)

    def display_reservations(self) -> None:
        """
        Displays all reservations in a human-readable format
        """
        print("Customer\t\tDate & Time\t\tNo. of People")
        for reservation in self.table_reservations:
            print(
                f"{reservation.customer.name}\t{reservation.reservation_time.strftime('%d-%m-%Y %I:%M %p')}\t{reservation.no_of_people}"
            )

    def customer_order(self, order: Order) -> None:
        """
        Takes order of a customer
        """
        self.customer_orders.append(order)

    def customer_bill(self, order: Order) -> None:
        """
        Displays order reciept and total bill, with added GST (18%).
        """
        print("Customer:", order.customer.name)
        print("\nItems\tQuantity\tPrice")
        bill = 0
        for order_item in order.order_items:
            print(
                f"{order_item.menu_item.name}\t{order_item.quantity}\t\tRs. {order_item.menu_item.price}"
            )
            bill += order_item.menu_item.price * order_item.quantity

        # add gst
        gst = 0.18
        print(f"\nGST\t\t\t{gst*100}%")
        bill += bill * gst

        print(f"\nTotal Bill\t\tRs. {bill}")


if __name__ == "__main__":
    # initialize restaurant
    restaurant = Restaurant()
    biryani = MenuItem("Biryani", 200)
    burger = MenuItem("Burger", 250)
    pepsi = MenuItem("Pepsi", 100)
    restaurant.add_item_to_menu(biryani)
    restaurant.add_item_to_menu(burger)
    restaurant.add_item_to_menu(pepsi)

    # Display Menu
    restaurant.display_menu()

    # initialize customer
    customer = Customer("Mustansir Muzaffar")

    # place reservation
    restaurant.book_reservation(Reservation(customer, datetime.now(), 2))
    restaurant.book_reservation(
        Reservation(customer, datetime(2023, 3, 10, 12, 0, 0), 1)
    )

    # Display reservations
    restaurant.display_reservations()

    # create orders
    order1 = Order(customer, [OrderItem(biryani, 2), OrderItem(pepsi, 1)])
    order2 = Order(customer, [OrderItem(burger, 1), OrderItem(pepsi, 2)])

    # place orders
    restaurant.customer_order(order1)
    restaurant.customer_order(order2)

    # print reciepts
    restaurant.customer_bill(order1)
    restaurant.customer_bill(order2)
