import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import uuid

def generate_sales_report(orders):
    if len(orders) > 0:
        total_sales, best_seller, worst_seller = calculate_sales_report(orders)
        st.write(f"Total Sales: RM{total_sales:.2f}")
        st.write(f"Best-Selling Coffee: {best_seller}")
        st.write(f"Worst-Selling Coffee: {worst_seller}")
        
        sales_df = pd.DataFrame(orders)
        chart = alt.Chart(sales_df).mark_bar().encode(
            x='coffee_type',
            y='sum(price)',
            color='coffee_type'
        ).properties(title='Sales per Coffee Type')

        st.altair_chart(chart, use_container_width=True)

promotions = {"DISCOUNT10": 0.1}  # Example promo code
def apply_promo_code(order, code):
    if code in promotions:
        discount = promotions[code]
        order["price"] *= (1 - discount)
        st.success(f"Promo applied! {int(discount*100)}% off!")
    else:
        st.warning("Invalid promo code.")

inventory_cost = {
    "coffee_beans": 0.05,  # Cost per gram
    "milk": 0.02,          # Cost per ml
    "sugar": 0.01,         # Cost per gram
    "cups": 0.10           # Cost per cup
}

def collect_feedback(order_id):
    feedback = st.text_area(f"Leave feedback for Order {order_id}")
    rating = st.slider("Rate your coffee", min_value=1, max_value=5)
    if st.button("Submit Feedback"):
        st.session_state.order_history[order_id].append({"feedback": feedback, "rating": rating})
        st.success("Feedback submitted successfully!")

def update_inventory(item, quantity):
    if item in st.session_state.inventory:
        if st.session_state.inventory[item] >= quantity:
            st.session_state.inventory[item] -= quantity
            # Low stock alert
            if st.session_state.inventory[item] < 0.2 * inventory[item]:
                st.warning(f"Low stock alert: Please restock {item}!")
        else:
            st.error(f"Not enough {item} in stock!")

def calculate_profit(orders):
    revenue = sum(order["price"] for order in orders)
    cost = 0

    for order in orders:
        quantity = order["quantity"]
        # Assume each coffee uses:
        # - 10g of coffee beans
        # - 200ml of milk if "Milk" is an add-on
        # - 10g of sugar if "Extra Sugar" is an add-on
        cost += quantity * (10 * inventory_cost["coffee_beans"] + inventory_cost["cups"])
        if "Milk" in order["add_ons"]:
            cost += quantity * 200 * inventory_cost["milk"]
        if "Extra Sugar" in order["add_ons"]:
            cost += quantity * 10 * inventory_cost["sugar"]

    profit = revenue - cost
    return revenue, cost, profit

if 'order_history' not in st.session_state:
    st.session_state.order_history = {}

# Initialize storage for user data (temporary storage for example purposes)
if 'users' not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "adminpass", "role": "admin"},
        "customer": {"password": "custpass", "role": "customer"}
    }

if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"  # Start with the login page

# Define initial data for the app
menu = {
    "Americano": 2.5,
    "Cappuccino": 3.0,
    "Latte": 3.5,
    "Caramel Macchiato": 4.0
}

inventory = {
    "coffee_beans": 1000,  # in grams
    "milk": 500,           # in milliliters
    "sugar": 200,          # in grams
    "cups": 100            # count
}

# Initialize session state for orders and inventory
if 'orders' not in st.session_state:
    st.session_state.orders = []

if 'inventory' not in st.session_state:
    st.session_state.inventory = inventory

# Helper functions
def generate_order_id():
    return str(uuid.uuid4())[:8]

def update_inventory(item, quantity):
    # Only admins should see the restock alert
    if st.session_state["user"]["role"] == "admin":
        if item in st.session_state.inventory:
            st.session_state.inventory[item] -= quantity
            if st.session_state.inventory[item] < 0.2 * inventory[item]:
                st.warning(f"Low stock alert: Please restock {item}!")
    else:
        # For customers, just update inventory without alerting them
        if item in st.session_state.inventory:
            st.session_state.inventory[item] -= quantity

def calculate_sales_report(orders):
    sales_df = pd.DataFrame(orders)
    total_sales = sales_df['price'].sum()
    coffee_sales = sales_df['coffee_type'].value_counts()
    best_seller = coffee_sales.idxmax()
    worst_seller = coffee_sales.idxmin()
    return total_sales, best_seller, worst_seller

# User authentication
def login(username, password):
    if username in st.session_state.users and st.session_state.users[username]["password"] == password:
        st.session_state["user"] = {"username": username, "role": st.session_state.users[username]["role"]}
        st.session_state["logged_in"] = True
        st.session_state["current_page"] = "app"  # Redirect to the app page
    else:
        st.error("Invalid username or password.")

# Account creation
def create_account(username, password, role="customer"):
    if username in st.session_state.users:
        st.warning("Username already exists. Choose a different username.")
    else:
        st.session_state.users[username] = {"password": password, "role": role}
        st.success("Account created successfully! Please login.")
        st.session_state.current_page = "login"

# Login Page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(username, password)
    st.button("Create an Account", on_click=lambda: set_page("register"))

# Registration Page
def register_page():
    st.title("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    if st.button("Sign Up"):
        if new_username and new_password:
            create_account(new_username, new_password)
        else:
            st.warning("Please fill out both fields.")
    st.button("Back to Login", on_click=lambda: set_page("login"))

def about_page():
    st.title("About This App")
    st.write("This app is developed as part of a university project for managing coffee shop operations.")
    st.write("### Team Members:")
    st.write("- Muhammad Afiq bin Josi Rizal - 22004193")

# Main Application Page with Sidebar Navigation
def app_page():
    user_role = st.session_state["user"]["role"]
    username = st.session_state["user"]["username"]

    # Sidebar with navigation options
    st.sidebar.header(f"Welcome, {username} ({user_role})")
    sidebar_option = st.sidebar.radio("Navigate", ["Home", "About Page"])

    # Navigate based on sidebar selection
    if sidebar_option == "About Page":
        about_page()
    else:
        if user_role == "customer":
            # Existing customer functionalities
            st.title("Place an Order")
            st.sidebar.header("Menu")
            for coffee, price in menu.items():
                st.sidebar.write(f"{coffee}: RM{price:.2f}")
            
            coffee_type = st.selectbox("Select Coffee Type", list(menu.keys()))
            size = st.selectbox("Select Size", ["Small", "Medium", "Large"])
            add_ons = st.multiselect("Add-ons", ["Extra Sugar", "Milk"])
            quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1)

            promo_code = st.text_input("Enter Promo Code (Optional)")

            # Initialize the order object before applying promo code
            order_id = generate_order_id()
            price = menu[coffee_type] * quantity
            order = {
                "order_id": order_id,
                "coffee_type": coffee_type,
                "size": size,
                "add_ons": add_ons,
                "quantity": quantity,
                "price": price,
                "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Preparing"
            }

            if promo_code:
                apply_promo_code(order, promo_code)  # Apply the promo code here

            if st.button("Place Order"):
                st.session_state.orders.append(order)
                if username not in st.session_state.order_history:
                    st.session_state.order_history[username] = []
                st.session_state.order_history[username].append(order)

                st.success(f"Order placed successfully! Your order ID is {order_id}.")
                st.write(f"Estimated Preparation Time: {5 + quantity * 2} minutes")
                update_inventory("coffee_beans", quantity * 10)
                update_inventory("cups", quantity)
                if "Milk" in add_ons:
                    update_inventory("milk", quantity * 200)  # Update milk for orders with milk
                if "Extra Sugar" in add_ons:
                    update_inventory("sugar", quantity * 10)  # Update sugar for orders with extra sugar

            # Notification Section for Pickup
            st.header("Pickup Notifications")
            notifications = [
                order for order in st.session_state.order_history.get(username, [])
                if order["status"] == "Ready"
            ]
            if notifications:
                st.success("The following orders are ready for pickup:")
                for order in notifications:
                    st.write(f"Order ID: {order['order_id']} - {order['coffee_type']} ({order['size']})")
            else:
                st.info("No orders are ready for pickup yet.")

            # Order History
            st.header("Order History")
            if username in st.session_state.order_history and st.session_state.order_history[username]:
                order_df = pd.DataFrame(st.session_state.order_history[username])
                st.dataframe(order_df[["order_id", "coffee_type", "size", "quantity", "price", "status", "order_time"]])
            else:
                st.write("No orders placed yet.")

        elif user_role == "admin":
            # Existing admin functionalities
            st.title("Admin Dashboard")
            st.header("Order Management")

            # Admin: Mark Orders as Ready
            if user_role == "admin":  # Only admins can mark orders as ready
                if len(st.session_state.orders) > 0:
                    for order in st.session_state.orders:
                        if order["status"] == "Preparing":
                            st.write(f"Order ID: {order['order_id']} - {order['coffee_type']} ({order['size']})")
                            if st.button(f"Mark as Ready - {order['order_id']}"):
                                order["status"] = "Ready"
                                st.success(f"Order {order['order_id']} marked as ready!")
                else:
                    st.info("No active orders to manage.")
            
            # Admin: Sales Report
            if user_role == "admin":  # Only admins can view the sales report
                if len(st.session_state.orders) > 0:
                    total_sales, best_seller, worst_seller = calculate_sales_report(st.session_state.orders)
                    st.write(f"Total Sales: RM{total_sales:.2f}")
                    st.write(f"Best-Selling Coffee: {best_seller}")
                    st.write(f"Least-Selling Coffee: {worst_seller}")
                    sales_df = pd.DataFrame(st.session_state.orders)
                    chart = alt.Chart(sales_df).mark_bar().encode(
                        x='coffee_type',
                        y='price',
                        color='coffee_type'
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.write("No sales data available.")

            # Admin: Inventory Management
            st.header("Inventory Management")
            if st.checkbox("Show Inventory"):
                st.write("Current Inventory Levels:")
                st.write(st.session_state.inventory)

            if st.button("Restock Inventory"):
                for item in st.session_state.inventory:
                    st.session_state.inventory[item] += 100
                st.success("Inventory has been restocked.")
        
    if st.sidebar.button("Logout"):
        logout()

# Logout
def logout():
    st.session_state["logged_in"] = False
    del st.session_state["user"]
    st.session_state["current_page"] = "login"
    st.success("Logged out successfully!")

# Set the current page
def set_page(page_name):
    st.session_state.current_page = page_name

# Page routing
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    if st.session_state.current_page == "login":
        login_page()
    elif st.session_state.current_page == "register":
        register_page()
