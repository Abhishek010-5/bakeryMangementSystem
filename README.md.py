# bakeryMangementSystem
import sqlite3
from pywebio.input import *
from pywebio.output import *

# Connect to SQLite database
conn = sqlite3.connect("bakery.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Orders (
    id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    total REAL NOT NULL
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS OrderItems (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders (id),
    FOREIGN KEY (product_id) REFERENCES Products (id)
)
"""
)


# Function to add a product to the inventory
def add_product(name, price, quantity):
    cursor.execute(
        "INSERT INTO Products (name, price, quantity) VALUES (?, ?, ?)",
        (name, price, quantity),
    )
    conn.commit()
    put_text("Product added successfully.")


# Function to display all products in the inventory
def display_products():
    cursor.execute("SELECT * FROM Products")
    products = [['ID',"Poduct",'Price','Qty']]
    products += cursor.fetchall()
    if not products:
        put_text("No products in inventory.")
    else:
        put_text("Inventory:")
        # for product in products:
        #     put_table(
        #         f"Product ID: {product[0]}, Product: {product[1]}, Price: {product[2]}, Quantity: {product[3]}"
        #     )
        put_table(products)


# Function to place a new order
def place_order(customer_name):
    items = []
    while True:
        display_products()
        product_id = input("Enter product ID: ",NUMBER)
        quantity = input("Enter quantity: ",NUMBER)
        items.append((product_id, quantity))
        cont = input("Add another product? (y/n): ")
        if cont.lower() != "y":
            break

    total = 0
    for item in items:
        cursor.execute("SELECT price FROM Products WHERE id=?", (item[0],))
        price = cursor.fetchone()[0]
        total += price * item[1]

    # Reduce quantity of products in inventory
    for item in items:
        cursor.execute(
            "UPDATE Products SET quantity = quantity - ? WHERE id = ?",
            (item[1], item[0]),
        )

    cursor.execute(
        "INSERT INTO Orders (customer_name, total) VALUES (?, ?)",
        (customer_name, total),
    )
    order_id = cursor.lastrowid

    for item in items:
        cursor.execute(
            "INSERT INTO OrderItems (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (order_id, item[0], item[1]),
        )

    conn.commit()
    put_text("Order placed successfully. Grand Total:", total)


# Function to refill the inventory
def refill_inventory():
    display_products()
    product_id = input("Enter product ID to refill: ",NUMBER)
    quantity = input("Enter quantity to add: ",NUMBER)
    cursor.execute(
        "UPDATE Products SET quantity = quantity + ? WHERE id = ?",
        (quantity, product_id),
    )
    conn.commit()
    put_text("Inventory refilled successfully.")


# Function to display orders with detailed information about what products each customer bought and their quantities
def display_orders():
    cursor.execute(
        """
        SELECT Orders.customer_name, OrderItems.quantity, Products.name, Products.price, Orders.total
        FROM Orders
        JOIN OrderItems ON Orders.id = OrderItems.order_id
        JOIN Products ON OrderItems.product_id = Products.id
        ORDER BY Orders.customer_name
    """
    )
    orders = cursor.fetchall()
    if not orders:
        put_text("No orders placed yet.")
    else:
        final = [['Customer Name','Product','Quantity','Price','Total']]
        the_final_customer_list =  []
        current_customer = None
        for order in orders:
            customer_name, quantity, product_name, price, total = order
            if current_customer != customer_name:
                if current_customer:
                    current_total
                # put_text(f"\nCustomer: {customer_name}")
                current_customer = customer_name
                current_total = total
            # put_text(f"Product -> {product_name}, Quantity -> {quantity}, Price -> {price}")
            current_total += quantity * price
        # put_text(f"Total -> {current_total}")
            detail = [current_customer,product_name,quantity,price,total]
            the_final_customer_list.append(detail)
        put_table(final + the_final_customer_list)


# Main function to interact with the user
def main():
    consumer_choice = {
        "Add Product": "1",
        "Display Products": "2",
        "Place Order": "3",
        "Refill Inventory": "4",
        "Display Orders": "5",
        "Exit": "Exit",
    }
    put_text("\nBakery Management System")
    while True:
        choice = select("Enter your choice: ", consumer_choice)

        if consumer_choice[choice] == "1":
            name = input("Enter product name: ", type=TEXT)
            price = input("Enter product price: ", NUMBER)
            quantity = input("Enter product quantity: ", NUMBER)
            add_product(name, price, quantity)

        elif consumer_choice[choice] == "2":
            display_products()

        elif consumer_choice[choice] == "3":
            customer_name = input("Enter customer name: ")
            place_order(customer_name)

        elif consumer_choice[choice] == "4":
            refill_inventory()

        elif consumer_choice[choice] == "5":
            display_orders()

        elif consumer_choice[choice] == "Exit":
            put_text("Exited")
            break

        else:
            print("Invalid choice. Please try again.")

    conn.close()


if __name__ == "__main__":
    main()
