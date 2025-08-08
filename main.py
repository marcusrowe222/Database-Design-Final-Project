import psycopg2
from psycopg2 import sql

# Database connection class
class Database:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cur = None

    def connect(self):
        if self.conn is None:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cur = self.conn.cursor()

    def disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        self.cur = None
        self.conn = None

    def call_proc(self, procname, params):
        self.connect()
        self.cur.callproc(procname, params)
        result = self.cur.fetchall()
        self.conn.commit()
        return result


    def execute_query(self, query, params=None):
        self.connect()
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur.fetchall()

# Login function
def login(db):
    while True:
        print("\n=== Login Menu: ===")
        print("1. Customer Login")
        print("2. Staff Login")
        print("0. Return to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == '0':
            return None  # Exit login

        if choice == '1':
            user_type = 'customer'
        elif choice == '2':
            user_type = 'staff'
        else:
            print("Invalid selection. Please try again.\n")
            continue

        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        try:
            # Call the login stored procedure
            result = db.call_proc('login', [username, password, user_type])
            
            if result and len(result) > 0 and result[0][0]:  # success = True
                user_id = result[0][1]
                print(f"\nLogin successful! Welcome, {username}")
                return (user_type, username, user_id)
            else:
                print("Login failed. Invalid credentials.\n")

        except Exception as e:
            print("An error occurred during login:", e)

# Registration function
def register(db):
    print("\n=== Register ===")
    username = input("Choose a username: ")
    password = input("Choose a password: ")
    first_name = input("First name: ")
    last_name = input("Last name: ")
    street = input("Street address: ")
    city = input("City: ")
    state = input("State: ")
    zipcode = input("Zip code: ")

    try:
        db.call_proc('register_customer', [username, password, first_name, last_name, street, city, zipcode])
        print(f"User '{username}' registered successfully!")
    except psycopg2.errors.UniqueViolation:
        print("Username already exists. Please try again.")
    except Exception as e:
        print(f"Error during registration: {e}")

# Credit Card Management
def manage_credit_cards(db, customer_id):
    try:
        #View existing cards
        cards = db.call_proc("view_credit_cards", (customer_id,))
        print("\nYour credit cards:")
        if not cards:
            print("  No cards on file.")
        else:
            for i, card in enumerate(cards, start=1):
                print(f"  {i}. {card[0]} (Expires: {card[1]})")

        print("\nAdd or remove a credit card?")
        print("1. Add credit card")
        print("2. Remove credit card")
        print("3. Back to main menu")
        choice = input("Choice (1-3): ").strip()

        if choice == "1":
            card_num = input("Enter credit card number: ").strip()
            exp_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
            db.call_proc("add_credit_card", (customer_id, card_num, exp_date))
            print("Credit card added successfully.")

        elif choice == "2":
            card_num = input("Enter the credit card number to remove: ").strip()
            db.call_proc("remove_credit_card", (customer_id, card_num))
            print("Credit card removed successfully.")

        elif choice == "3":
            print("Returning to main menu...")
            return

        else:
            print("Invalid choice.")
    except Exception as e:
        print(f"Error managing credit cards: {e}")

# Purchasing
def make_purchase(db, customer_id):
    try:
        # Get product info
        product_id = int(input("Enter the Product ID you wish to buy: "))
        result = db.call_proc("get_product_by_id", [product_id])
        if not result:
            print("Error: Product not found.")
            return

        product = result[0] 
        product_id, product_name, product_category, product_price, product_qty = product

        print(f"\nProduct: {product_name} (Category: {product_category}), Price: ${product_price:.2f}, In Stock: {product_qty}\n")

        # Get quantity
        quantity = int(input("Enter the quantity you want to buy: "))
        if quantity <= 0:
            print("Quantity must be positive.")
            return
        if quantity > product_qty:
            print("Not enough stock available.")
            return

        # Select credit card
        cards = db.call_proc("view_credit_cards", (customer_id,))
        if not cards:
            print("No credit cards found. Please add a card first.")
            return

        print("\nYour credit cards:")
        for i, card in enumerate(cards, 1):
            print(f"{i}. {card[0]} (expires {card[1]})")
        
        card_choice = int(input("Select a card to use (single number): "))
        if card_choice < 1 or card_choice > len(cards):
            print("Invalid card selection.")
            return
        selected_card = cards[card_choice - 1][0]

        # Confirm purchase
        total = product_price * quantity
        print(f"\nConfirm Purchase:")
        print(f"  {quantity} x {product_name} @ ${product_price:.2f} = ${total:.2f}")
        print(f"  Using card: {selected_card}")
        confirm = input("Confirm purchase? (y/n): ").strip().lower()

        if confirm != 'y':
            print("Purchase cancelled.")
            return

        # Record purchase and update inventory
        db.call_proc("create_purchase", (customer_id, product_id, quantity, selected_card))
        print("Purchase successful!")

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except Exception as e:
        print("Error during purchase:", e)

# User Purchase History
def view_purchase_history(db, customer_id):
    try:
        results = db.call_proc('user_purchase_history', [customer_id])
        if not results:
            print("No purchase history found.")
            return

        print("\nPurchase History:")
        print("-" * 80)
        print(f"{'Purchase ID':<12} {'Date':<20} {'Product ID':<10} {'Product Name':<25} {'Qty':<5} {'Unit Price':<12} {'Total Price':<12}")
        print("-" * 80)

        for row in results:
            purchase_id, purchase_date, product_id, product_name, quantity, unit_price, total_price = row
            print(f"{purchase_id:<12} {purchase_date.strftime('%Y-%m-%d %H:%M'):<20} {product_id:<10} {product_name:<25} {quantity:<5} ${unit_price:<11.2f} ${total_price:<11.2f}")

        print("-" * 80)

    except Exception as e:
        print(f"Error viewing purchase history: {e}")

# Staff Purchase History
def staff_view_purchase_history(db):
    try:
        # Call the stored procedure 
        purchases = db.call_proc("view_purchase_history", [])

        if not purchases:
            print("No purchase history found.")
            return

        # Print header
        print("\nAll Purchases History:")
        print("-" * 120)
        header = f"{'Purchase ID':<12} {'Date':<12} {'Customer ID':<12} {'First Name':<15} {'Last Name':<15} {'Product ID':<12} {'Product Name':<25} {'Qty':<5} {'Unit Price':<10} {'Total Price':<12}"
        print(header)
        print("-" * 120)

        # Print rows
        for row in purchases:
            purchase_id, purchase_date, customer_id, first_name, last_name, product_id, product_name, quantity, unit_price, total_price = row
            print(f"{purchase_id:<12} {purchase_date.strftime('%Y-%m-%d'):<12} {customer_id:<12} {first_name:<15} {last_name:<15} {product_id:<12} {product_name:<25} {quantity:<5} ${unit_price:<9.2f} ${total_price:<11.2f}")

        print("-" * 120)

    except Exception as e:
        print(f"Error viewing purchase history: {e}")

# Add a product
def add_product(db):
    print("\n=== Add New Product ===")
    name = input("Product Name: ").strip()
    category = input("Category: ").strip()

    while True:
        try:
            price = float(input("Price: ").strip())
            if price < 0:
                print("Price cannot be negative. Try again.")
                continue
            break
        except ValueError:
            print("Invalid price. Please enter a valid number.")

    while True:
        try:
            quantity = int(input("Quantity: ").strip())
            if quantity < 0:
                print("Quantity cannot be negative. Try again.")
                continue
            break
        except ValueError:
            print("Invalid quantity. Please enter a valid integer.")

    try:
        db.call_proc("add_product", (name, category, price, quantity))
        print(f"Product '{name}' added successfully!")
    except Exception as e:
        print(f"Error adding product: {e}")

def customer_menu(db, customer_id):
    while True:
        print("\nCustomer Menu")
        print("1. View Products")
        print("2. View Purchase History")
        print("3. Make Purchase")
        print("4. Manage Credit Cards")
        print("5. Logout")
        choice = input("Select an option: ")

        if choice == '1':
            view_products(db)
        elif choice == '2':
            view_purchase_history(db, customer_id)
        elif choice == '3':
            make_purchase(db, customer_id)
        elif choice == '4':
            manage_credit_cards(db, customer_id)
        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid Selection")

def staff_menu(db, staff_id):
    while True:
        print("\n === Staff Menu ===")
        print("1. View Inventory")
        print("2. View Purchase History")
        print("3. Add Product")
        print("4. Logout")
        choice = input("Select an option: ")
        if choice == '1':
            view_products(db)
        elif choice == '2':
            staff_view_purchase_history(db)
        elif choice == '3':
            add_product(db)
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid Selection")

def view_products(db):
    try:
        result = db.call_proc("view_products", [])
        if not result:
            print("No products found.")
            return

        print("\nAvailable Products:")
        print("-" * 75)
        print(f"{'ID':<5} {'Name':<25} {'Category':<15} {'Price':<10} {'Qty':<5}")
        print("-" * 75)
        for row in result:
            product_id, name, category, price, quantity = row
            print(f"{product_id:<5} {name:<25} {category:<15} ${price:<10.2f} {quantity:<5}")
        print("-" * 75)

    except Exception as e:
        print(f"Error viewing products: {e}")

def main():
    db = Database(dbname="postgres", user="postgres", password="password")

    print("=== Welcome to the E-Commerce Database System ===")

    while True:
        print("\nLogin or register to continue")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Select an option (1/2/3): ")

        if choice == '1':
            loginResult = login(db)
            if loginResult:
                user_type, username, user_id = loginResult
                if user_type == 'customer':
                    customer_menu(db, user_id)
                elif user_type == 'staff':
                    staff_menu(db, user_id)
                else:
                    print("Unrecognized role.")
            else:
                print("Login failed. Please try again.")
        elif choice == '2':
            register(db)
        elif choice == '3':
            print("Goodbye!")
            db.disconnect()
            break
        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()

