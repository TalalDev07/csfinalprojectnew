import mysql.connector 
from datetime import datetime 
import hashlib 
import os
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
 
# connecting db --------------------------------------------- 
 
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Talal"
)

cur = con.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS carnival_pos")
cur.execute("USE carnival_pos")
 
 
def setup_database():  
    cur.execute("""  
        CREATE TABLE IF NOT EXISTS stalls (  
            stall_id INT AUTO_INCREMENT PRIMARY KEY,  
            stall_name VARCHAR(255) NOT NULL UNIQUE,  
            password_hash VARCHAR(64) NOT NULL,  
            stall_type VARCHAR(255) NOT NULL  
        )  
    """)  
  
    cur.execute("""  
        CREATE TABLE IF NOT EXISTS items (  
            item_id INT AUTO_INCREMENT PRIMARY KEY,  
            stall_id INT NOT NULL,  
            item_name VARCHAR(255) NOT NULL,  
            price DECIMAL(10,3) NOT NULL,  
            description TEXT,  
            image_path TEXT,  
            is_active INT NOT NULL DEFAULT 1,  
  
            FOREIGN KEY (stall_id)  
            REFERENCES stalls(stall_id)  
        )  
    """)  
  
    cur.execute("""  
        CREATE TABLE IF NOT EXISTS orders (  
            order_id INT AUTO_INCREMENT PRIMARY KEY,  
            stall_id INT NOT NULL,  
            total_price DECIMAL(10,3) NOT NULL,  
            timestamp DATETIME NOT NULL,  
  
            FOREIGN KEY (stall_id)  
            REFERENCES stalls(stall_id)  
        )  
    """)  
  
    cur.execute("""  
        CREATE TABLE IF NOT EXISTS order_items (  
            order_item_id INT AUTO_INCREMENT PRIMARY KEY,  
            order_id INT NOT NULL,  
            item_id INT NOT NULL,  
            quantity INT NOT NULL,  
            unit_price DECIMAL(10,3) NOT NULL,  
  
            FOREIGN KEY (order_id)  
            REFERENCES orders(order_id),  
  
            FOREIGN KEY (item_id)  
            REFERENCES items(item_id)  
        )  
    """)  
  
    con.commit() 
 
setup_database()  # Runs every startup. Creates database table if it doesn't exist. 
 
 
# structures ---------------------------------------------- 
 
cart = {}  # Dictionary storing item_id as key and quantity as value. Used to create a receipt. 
 
 
# stall functions --------------------------------------------- 
 
def hash_password(password): 
    # converts password into a hash before storing/comparing it 
 
    return hashlib.sha256(password.encode()).hexdigest() 
 
 
def create_stall(stall_name, password, stall_type): 
    # creates a new stall/project 
 
    password_hash = hash_password(password) 
 
    cur.execute(""" 
        INSERT INTO stalls ( 
            stall_name, 
            password_hash, 
            stall_type 
        ) 
        VALUES (%s, %s, %s) 
    """, ( 
        stall_name, 
        password_hash, 
        stall_type 
    )) 
 
    con.commit() 
 
    return cur.lastrowid 
 
 
def get_stalls(): 
    # returns all stalls to the stall selection screen 
 
    cur.execute(""" 
        SELECT 
            stall_id, 
            stall_name, 
            stall_type 
        FROM stalls 
        ORDER BY stall_name 
    """) 
 
    stalls = cur.fetchall() 
 
    return stalls 
 
 
def get_stall(stall_id): 
    # returns one specific stall 
 
    cur.execute(""" 
        SELECT 
            stall_id, 
            stall_name, 
            stall_type 
        FROM stalls 
        WHERE stall_id = %s 
    """, (stall_id,)) 
 
    stall = cur.fetchone() 
 
    return stall 
 
 
def verify_stall_password(stall_id, password): 
    # checks whether the entered stall password is correct 
 
    entered_hash = hash_password(password) 
 
    cur.execute(""" 
        SELECT password_hash 
        FROM stalls 
        WHERE stall_id = %s 
    """, (stall_id,)) 
 
    result = cur.fetchone() 
 
    if result is None: 
        return False 
 
    stored_hash = result[0] 
 
    return entered_hash == stored_hash 
 
 
# item functions --------------------------------------------- 
 
def add_item(stall_id, name, price, description, imagepath): 
    # adds new item in db and assigns it to a stall 
 
    cur.execute(""" 
        INSERT INTO items ( 
            stall_id, 
            item_name, 
            price, 
            description, 
            image_path 
        ) 
        VALUES (%s, %s, %s, %s, %s) 
    """, ( 
        stall_id, 
        name, 
        price, 
        description, 
        imagepath 
    )) 
 
    con.commit() 
 
    return cur.lastrowid 
 
def get_card_image(image_path):
    # resize product image to fit inside menu card

    if not image_path or not os.path.exists(image_path):
        return None

    image = Image.open(image_path)
    image = ImageOps.fit(image, (240, 180))

    return image
 
def get_items(stall_id): 
    # returns all active items belonging to one stall to main menu 
 
    cur.execute(""" 
        SELECT * 
        FROM items 
        WHERE stall_id = %s 
        AND is_active = 1 
        ORDER BY item_name 
    """, (stall_id,)) 
 
    items = cur.fetchall() 
 
    return items 
 
 
def get_item(item_id): 
    # returns a specific item from db to menu/receipt 
 
    cur.execute(""" 
        SELECT * 
        FROM items 
        WHERE item_id = %s 
    """, (item_id,)) 
 
    item = cur.fetchone() 
 
    return item 
 
 
def update_item(item_id, name, price, description, imagepath): 
    # edits an existing item's information 
 
    cur.execute(""" 
        UPDATE items 
        SET item_name = %s, 
            price = %s, 
            description = %s, 
            image_path = %s 
        WHERE item_id = %s 
    """, ( 
        name, 
        price, 
        description, 
        imagepath, 
        item_id 
    )) 
 
    con.commit() 
 
 
def delete_item(item_id): 
    # hides item from menu without deleting old receipt information 
 
    cur.execute(""" 
        UPDATE items 
        SET is_active = 0 
        WHERE item_id = %s 
    """, (item_id,)) 
 
    con.commit() 
 
 
# order functions --------------------------------------------- 
 
def add_to_order(item_id): 
    # adds new item into the cart 
 
    item = get_item(item_id) 
 
    if item is None or item[6] == 0: 
        return False 
 
    if item_id in cart: 
        cart[item_id] += 1 
    else: 
        cart[item_id] = 1 
 
    print(cart) 
 
    return True 
 
 
def remove_from_order(item_id): 
    # removes item currently in cart 
 
    if item_id in cart: 
        if cart[item_id] == 1: 
            cart.pop(item_id) 
        else: 
            cart[item_id] -= 1 
 
    print(cart) 
 
 
def calculate_total(): 
    # calc total bill -- gets cart item, gets its price, 
    # multiplies by quantity, updates running total. 
 
    total = 0 
 
    for item_id, quantity in cart.items(): 
        item = get_item(item_id) 
 
        if item is not None: 
            price = item[3] 
            subtotal = price * quantity 
            total += subtotal 
 
    return round(total, 3) 
 
 
def complete_order(stall_id): 
    # complete the order, make a receipt id for it, 
    # insert items into one and receipts into one table. 
 
    if not cart: 
        return None 
 
    total = calculate_total() 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
 
    try: 
        cur.execute(""" 
            INSERT INTO orders ( 
                stall_id, 
                total_price, 
                timestamp 
            ) 
            VALUES (%s, %s, %s) 
        """, ( 
            stall_id, 
            total, 
            timestamp 
        )) 
 
        order_id = cur.lastrowid 
 
        for item_id, quantity in cart.items(): 
            item = get_item(item_id) 
 
            if item is None: 
                raise ValueError("An item in the cart no longer exists.") 
 
            item_stall_id = item[1] 
            unit_price = item[3] 
 
            if item_stall_id != stall_id: 
                raise ValueError( 
                    "The cart contains an item belonging to another stall." 
                ) 
 
            cur.execute(""" 
                INSERT INTO order_items ( 
                    order_id, 
                    item_id, 
                    quantity, 
                    unit_price 
                ) 
                VALUES (%s, %s, %s, %s) 
            """, ( 
                order_id, 
                item_id, 
                quantity, 
                unit_price 
            )) 
 
        con.commit() 
        clear_order() 
 
        return order_id 
 
    except Exception: 
        con.rollback() 
        raise  

def download_receipt_pdf(order_id):
    # gets order information from database

    cur.execute("""
        SELECT orders.total_price, orders.timestamp,
               stalls.stall_name
        FROM orders, stalls
        WHERE orders.stall_id = stalls.stall_id
        AND orders.order_id = %s
    """, (order_id,))

    order = cur.fetchone()

    if order is None:
        return None

    total = order[0]
    date = order[1]
    stall_name = order[2]

    # gets items purchased in the order

    cur.execute("""
        SELECT items.item_name, order_items.quantity,
               order_items.unit_price
        FROM order_items, items
        WHERE order_items.item_id = items.item_id
        AND order_items.order_id = %s
    """, (order_id,))

    items = cur.fetchall()

    # creates receipts folder if it does not exist

    folder = "Receipts"
    os.makedirs(folder, exist_ok=True)

    # creates unique filename with date and order id

    date_text = date.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Receipt_{order_id}_{date_text}.pdf"
    filepath = os.path.join(folder, filename)

    # creates pdf

    pdf = canvas.Canvas(filepath, pagesize=(300, 500))

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 460, "CARNIVAL RECEIPT")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, 430, stall_name)
    pdf.drawString(40, 410, f"Order Number: {order_id}")
    pdf.drawString(40, 390, str(date))

    pdf.line(30, 375, 270, 375)

    y = 350

    for item in items:
        name = item[0]
        quantity = item[1]
        price = item[2]

        subtotal = quantity * price

        pdf.setFont("Helvetica", 10)
        pdf.drawString(30, y, f"{quantity}x {name[:18]}")
        pdf.drawRightString(270, y, f"{subtotal:.3f}")

        y -= 25

        # new page if receipt is too long
        if y < 70:
            pdf.showPage()
            y = 450

    pdf.line(30, y, 270, y)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(30, y - 25, "TOTAL:")
    pdf.drawRightString(270, y - 25, f"KWD {total:.3f}")

    pdf.setFont("Helvetica", 9)
    pdf.drawString(75, y - 55, "Thank you for visiting!")

    pdf.save()

    return filepath

def clear_order(): 
    # clear order from cart/complete for fresh new 
 
    cart.clear() 
    print(cart) 
 
def get_sales_report(stall_id):
    # returns total sales, orders and average order value

    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(total_price), 0)
        FROM orders
        WHERE stall_id = %s
    """, (stall_id,))

    result = cur.fetchone()

    total_orders = result[0]
    total_sales = result[1]

    if total_orders > 0:
        average_order = total_sales / total_orders
    else:
        average_order = 0

def get_best_selling_items(stall_id):
    # returns the top 5 items based on quantity sold

    cur.execute("""
        SELECT items.item_name, SUM(order_items.quantity)
        FROM order_items, items, orders
        WHERE order_items.item_id = items.item_id
        AND order_items.order_id = orders.order_id
        AND orders.stall_id = %s
        GROUP BY items.item_id, items.item_name
        ORDER BY SUM(order_items.quantity) DESC
        LIMIT 5
    """, (stall_id,))

    return cur.fetchall()