class Inventory:

    """
    A class to represent an inventory of items.
    """

    def __init__(self) -> None:
        self.items = {}

    def add_item(self, item_id: int, item_name: str, stock_count: int, price: float) -> None:
        """
        Adds the given item into the inventory. Raises an Exception
        if item with the given item_id already exists.
        """

        if item_id in self.items:
            raise Exception("Item already exists.")

        self.items[item_id] = {
            "item_name": item_name,
            "stock_count": stock_count,
            "price": price
        }

    def update_item(self, item_id: int, item_name: str = None, stock_count: int = None, price: float = None) -> None:
        """
        Updates an item with given item_id with the given fields. Raises an Exception
        if item with given item_id does not exist.
        """
        self.check_item_exists(item_id)

        item = self.items[item_id]
        if item_name:
            item['item_name'] = item_name
        if stock_count:
            item['stock_count'] = stock_count
        if price:
            item['price'] = price

    def check_item_details(self, item_id: int) -> str:
        """
        Returns a human-readable string for the item with the given item_id. Raises an Exception
        if item with given item_id does not exist.
        """

        self.check_item_exists(item_id)

        item = self.items[item_id]
        return f"""Item ID: {item_id}\nItem Name: {item['item_name']}\nStock Count: {item['stock_count']}\nPrice: ${item['price']}"""

    def increment_stock(self, item_id: int) -> None:
        """
        Increments the stock for the item with given item_id. Raises an Exception
        if item with given item_id does not exist.
        """
        self.check_item_exists(item_id)

        self.items[item_id]['stock_count'] += 1

    def decrement_stock(self, item_id: int) -> None:
        """
        Decrements the stock for the item with given item_id. Raises an Exception
        if item with given item_id does not exist.
        """
        self.check_item_exists(item_id)

        item = self.items[item_id]
        if item['stock_count'] == 0:
            raise Exception("Item stock count cannot be less than zero.")
        item['stock_count'] -= 1

    def delete_item(self, item_id: int) -> None:
        """
        Deletes an item from the inventory with the given item_id. Raises an Exception
        if item with given item_id does not exist.
        """
        self.check_item_exists(item_id)

        self.items.pop(item_id)

    def check_item_exists(self, item_id: int) -> None:
        """
        A helper function to check if the item with the given item_id exists in the inventory. Raises an Exception if it does not.
        """
        if item_id not in self.items:
            raise Exception("Item does not exist.")


# testing code
if __name__ == "__main__":

    inventory = Inventory()
    inventory.add_item(1, "Keyboard", 2, 9.99)
    inventory.add_item(2, "Mouse", 5, 2.00)
    print(inventory.check_item_details(1))
    inventory.update_item(1, price=5.99)
    print(inventory.check_item_details(1))
    inventory.decrement_stock(2)
    print(inventory.check_item_details(2))
    inventory.delete_item(1)
    inventory.check_item_details(1)  # should raise Exception
