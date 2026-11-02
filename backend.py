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
    password="mouli999"
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
 
setup_database()  # Creates database tables if they do not exist
 
 
# structures ---------------------------------------------- 
 
cart = {}  # Dictionary storing item_id as key and quantity as value.
 
 
# stall functions --------------------------------------------- 
 
def hash_password(password): 
    return hashlib.sha256(password.encode()).hexdigest() 
 
 
def create_stall(stall_name, password, stall_type): 
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
    cur.execute(""" 
        SELECT 
            stall_id, 
            stall_name, 
            stall_type 
        FROM stalls 
        ORDER BY stall_name 
    """) 
    return cur.fetchall() 
 
 
def get_stall(stall_id): 
    cur.execute(""" 
        SELECT 
            stall_id, 
            stall_name, 
            stall_type 
        FROM stalls 
        WHERE stall_id = %s 
    """, (stall_id,)) 
    return cur.fetchone() 
 
 
def verify_stall_password(stall_id, password): 
    entered_hash = hash_password(password) 
 
    cur.execute(""" 
        SELECT password_hash 
        FROM stalls 
        WHERE stall_id = %s 
    """, (stall_id,)) 
 
    result = cur.fetchone() 
    if result is None: 
        return False 
 
    return entered_hash == result[0] 
 
 
# item functions --------------------------------------------- 
 
def add_item(stall_id, name, price, description, imagepath): 
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
 
def get_card_image(image_path, size=(75, 75)):
    # Resizes and formats product image to fit inside menu card
    if not image_path:
        return None

    if not os.path.isabs(image_path):
        candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path)
        if os.path.exists(candidate):
            image_path = candidate

    if not os.path.exists(image_path):
        return None

    try:
        image = Image.open(image_path)
        return ImageOps.fit(image, size)
    except Exception:
        return None
 
def get_items(stall_id): 
    cur.execute(""" 
        SELECT * 
        FROM items 
        WHERE stall_id = %s 
        AND is_active = 1 
        ORDER BY item_name 
    """, (stall_id,)) 
    return cur.fetchall() 
 
 
def get_item(item_id): 
    cur.execute(""" 
        SELECT * 
        FROM items 
        WHERE item_id = %s 
    """, (item_id,)) 
    return cur.fetchone() 
 
 
def update_item(item_id, name, price, description, imagepath): 
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
    cur.execute(""" 
        UPDATE items 
        SET is_active = 0 
        WHERE item_id = %s 
    """, (item_id,)) 
 
    con.commit() 
 
 
# order functions --------------------------------------------- 
 
def add_to_order(item_id): 
    item = get_item(item_id) 
 
    if item is None or item[6] == 0: 
        return False 
 
    cart[item_id] = cart.get(item_id, 0) + 1 
    return True 
 
 
def remove_from_order(item_id): 
    if item_id in cart: 
        if cart[item_id] <= 1: 
            cart.pop(item_id) 
        else: 
            cart[item_id] -= 1 
 
 
def calculate_total(): 
    total = 0.0
    for item_id, quantity in cart.items(): 
        item = get_item(item_id) 
        if item is not None: 
            total += float(item[3]) * quantity 
 
    return round(total, 3) 
 
 
def complete_order(stall_id): 
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
 
            if item[1] != stall_id: 
                raise ValueError("Cart contains an item belonging to another stall.") 
 
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
                float(item[3]) 
            )) 
 
        con.commit() 
        clear_order() 
        return order_id 
 
    except Exception: 
        con.rollback() 
        raise  
 
def download_receipt_pdf(order_id):
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

    total = float(order[0])
    date = order[1]
    stall_name = order[2]

    cur.execute("""
        SELECT items.item_name, order_items.quantity,
               order_items.unit_price
        FROM order_items, items
        WHERE order_items.item_id = items.item_id
        AND order_items.order_id = %s
    """, (order_id,))

    items = cur.fetchall()

    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Receipts")
    os.makedirs(folder, exist_ok=True)

    if isinstance(date, str):
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date_text = date_obj.strftime("%Y-%m-%d_%H-%M-%S")
        except ValueError:
            date_text = date.replace(":", "-").replace(" ", "_")
    elif hasattr(date, "strftime"):
        date_text = date.strftime("%Y-%m-%d_%H-%M-%S")
    else:
        date_text = str(date).replace(":", "-").replace(" ", "_")

    filename = f"Receipt_{order_id}_{date_text}.pdf"
    filepath = os.path.join(folder, filename)

    pdf = canvas.Canvas(filepath, pagesize=(300, 500))

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 460, "CARNIVAL RECEIPT")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, 430, stall_name)
    pdf.drawString(40, 410, f"Order Number: #{order_id:04d}")
    pdf.drawString(40, 390, str(date))

    pdf.line(30, 375, 270, 375)

    y = 350
    for item in items:
        name = item[0]
        quantity = item[1]
        price = float(item[2])
        subtotal = quantity * price

        pdf.setFont("Helvetica", 10)
        pdf.drawString(30, y, f"{quantity}x {name[:18]}")
        pdf.drawRightString(270, y, f"{subtotal:.3f}")
        y -= 25

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
    cart.clear() 
 
def get_sales_report(stall_id):
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(total_price), 0)
        FROM orders
        WHERE stall_id = %s
    """, (stall_id,))

    result = cur.fetchone()
    total_orders = result[0]
    total_sales = float(result[1])
    average_order = (total_sales / total_orders) if total_orders > 0 else 0.0

    return total_orders, total_sales, average_order

def get_best_selling_items(stall_id):
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
