
import tkinter as tk
from tkinter import ttk, messagebox
import backend


# sample data
def ensure_initial_data():
    stalls = backend.get_stalls()
    if not stalls:
        b_id = backend.create_stall("Burger Station", "burger123", "food")
        backend.add_item(b_id, "Classic Cheeseburger", 3.500, "Beef patty with cheddar and sauce", "burger.png")
        backend.add_item(b_id, "Double Patty Burger", 4.750, "Two patties, extra cheese and bacon", "")
        backend.add_item(b_id, "Crispy French Fries", 1.250, "Golden salted potato fries", "")
        backend.add_item(b_id, "Soft Drink", 0.750, "Chilled soda can", "")

        s_id = backend.create_stall("Sweet Treats", "sweet123", "dessert")
        backend.add_item(s_id, "Chocolate Ice Cream", 1.500, "Rich creamy chocolate cone", "")
        backend.add_item(s_id, "Cotton Candy", 1.000, "Pink sugar cloud on a stick", "")
        backend.add_item(s_id, "Churros with Nutella", 2.250, "Cinnamon churros with dip", "")


class CarnivalApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Carnival POS System")
        self.geometry("1100x720")
        self.minsize(950, 600)
        self.configure(bg="#f1f5f9")

        # current stall
        self.current_stall_id = None
        self.current_stall_name = ""
        self.current_stall_type = ""

        # screens
        self.container = tk.Frame(self, bg="#f1f5f9")
        self.container.pack(fill="both", expand=True)

        
        self.frames = {
            "StallSelectionScreen": StallSelectionScreen(self.container, controller=self),
            "StallPOSScreen": StallPOSScreen(self.container, controller=self)
        }

        
        self.show_frame("StallSelectionScreen")

    def show_frame(self, page_name, **kwargs):
        for frame in self.frames.values():
            frame.pack_forget()

        active_frame = self.frames[page_name]
        active_frame.pack(fill="both", expand=True)

        if hasattr(active_frame, "on_show"):
            active_frame.on_show(**kwargs)


class StallSelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f1f5f9")
        self.controller = controller

        
        wrapper = tk.Frame(self, bg="#f1f5f9")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        
        card = tk.Frame(wrapper, bg="#ffffff", padx=40, pady=35, relief="solid", bd=1)
        card.pack()

        # Title
        tk.Label(
            card,
            text="Carnival POS System",
            font=("Helvetica", 24, "bold"),
            bg="#ffffff",
            fg="#0f172a"
        ).pack(pady=(0, 5))

        tk.Label(
            card,
            text="Select your stall to launch the POS terminal",
            font=("Helvetica", 12),
            bg="#ffffff",
            fg="#64748b"
        ).pack(pady=(0, 25))

        # stall dropdown
        tk.Label(
            card,
            text="Choose Stall:",
            font=("Helvetica", 11, "bold"),
            bg="#ffffff",
            fg="#1e293b",
            anchor="w"
        ).pack(fill="x", pady=(5, 2))

        self.stall_var = tk.StringVar()
        self.stall_dropdown = ttk.Combobox(
            card,
            textvariable=self.stall_var,
            font=("Helvetica", 12),
            state="readonly",
            width=32
        )
        self.stall_dropdown.pack(fill="x", pady=(0, 15), ipady=3)

        # password
        tk.Label(
            card,
            text="Stall Password:",
            font=("Helvetica", 11, "bold"),
            bg="#ffffff",
            fg="#1e293b",
            anchor="w"
        ).pack(fill="x", pady=(5, 2))

        self.password_entry = tk.Entry(
            card,
            font=("Helvetica", 12),
            show="•",
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            bd=1,
            relief="solid",
            width=32
        )
        self.password_entry.pack(fill="x", pady=(0, 5), ipady=4)
        self.password_entry.bind("<Return>", lambda e: self.login())

        # password hint
        self.hint_label = tk.Label(
            card,
            text="Default password for Burger Station: burger123",
            font=("Helvetica", 9, "italic"),
            bg="#ffffff",
            fg="#2563eb"
        )
        self.hint_label.pack(fill="x", pady=(0, 18))

        
        login_btn = tk.Button(
            card,
            text="Open POS Terminal",
            font=("Helvetica", 12, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            highlightbackground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.login
        )
        login_btn.pack(fill="x", pady=(0, 12))

        
        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=10)

        
        actions_row = tk.Frame(card, bg="#ffffff")
        actions_row.pack(fill="x")

        new_stall_btn = tk.Button(
            actions_row,
            text="+ Create New Stall",
            font=("Helvetica", 10, "bold"),
            bg="#f8fafc",
            fg="#334155",
            highlightbackground="#ffffff",
            cursor="hand2",
            padx=8,
            pady=4,
            command=self.open_create_stall_dialog
        )
        new_stall_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        test_login_btn = tk.Button(
            actions_row,
            text="Quick Test Login",
            font=("Helvetica", 10, "bold"),
            bg="#f8fafc",
            fg="#334155",
            highlightbackground="#ffffff",
            cursor="hand2",
            padx=8,
            pady=4,
            command=self.quick_test_login
        )
        test_login_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        self.stalls_data = []

    def on_show(self):
        self.refresh_stall_list()
        self.password_entry.delete(0, tk.END)

    def refresh_stall_list(self):
        self.stalls_data = backend.get_stalls()
        if self.stalls_data:
            options = [f"{s[1]} ({s[2].capitalize()})" for s in self.stalls_data]
            self.stall_dropdown["values"] = options
            self.stall_dropdown.current(0)
        else:
            self.stall_dropdown["values"] = ["No stalls available"]
            self.stall_dropdown.current(0)

    def login(self):
        if not self.stalls_data:
            messagebox.showwarning("No Stalls", "No stalls exist. Please create one.")
            return

        selected_idx = self.stall_dropdown.current()
        if selected_idx < 0 or selected_idx >= len(self.stalls_data):
            messagebox.showwarning("Selection Required", "Please choose a stall from the list.")
            return

        stall = self.stalls_data[selected_idx]
        stall_id = stall[0]
        stall_name = stall[1]
        stall_type = stall[2]
        password = self.password_entry.get()

        if not password:
            messagebox.showwarning("Password Required", "Please enter the stall password.")
            return

        if backend.verify_stall_password(stall_id, password):
            self.controller.current_stall_id = stall_id
            self.controller.current_stall_name = stall_name
            self.controller.current_stall_type = stall_type
            backend.clear_order()
            self.controller.show_frame("StallPOSScreen")
        else:
            messagebox.showerror("Access Denied", "Incorrect password. Try again.")

    def quick_test_login(self):
        if not self.stalls_data:
            ensure_initial_data()
            self.refresh_stall_list()

        if self.stalls_data:
            stall = self.stalls_data[0]
            self.controller.current_stall_id = stall[0]
            self.controller.current_stall_name = stall[1]
            self.controller.current_stall_type = stall[2]
            backend.clear_order()
            self.controller.show_frame("StallPOSScreen")

    def open_create_stall_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Stall")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.transient(self)
        dialog.grab_set()

        container = tk.Frame(dialog, bg="#ffffff", padx=25, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Create New Stall", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=(0, 15))

        tk.Label(container, text="Stall Name:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        name_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        name_entry.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(container, text="Password:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        pwd_entry = tk.Entry(container, font=("Helvetica", 11), show="•", bg="#ffffff", fg="#000000", bd=1, relief="solid")
        pwd_entry.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(container, text="Stall Type (e.g. food, drinks, dessert):", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        type_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        type_entry.insert(0, "food")
        type_entry.pack(fill="x", pady=(2, 15), ipady=3)

        def submit():
            name = name_entry.get().strip()
            pwd = pwd_entry.get().strip()
            stype = type_entry.get().strip() or "food"

            if not name or not pwd:
                messagebox.showerror("Error", "Name and password are required.", parent=dialog)
                return

            try:
                backend.create_stall(name, pwd, stype)
                messagebox.showinfo("Success", f"Stall '{name}' created!", parent=dialog)
                dialog.destroy()
                self.refresh_stall_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create stall: {e}", parent=dialog)

        tk.Button(
            container,
            text="Create Stall",
            font=("Helvetica", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            highlightbackground="#ffffff",
            command=submit
        ).pack(fill="x", pady=10)


class StallPOSScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller

        # header
        header = tk.Frame(self, bg="#ffffff", padx=20, pady=12, relief="solid", bd=1)
        header.pack(fill="x", side="top")

        tk.Button(
            header,
            text="Switch Stall",
            font=("Helvetica", 11, "bold"),
            bg="#f1f5f9",
            fg="#334155",
            highlightbackground="#ffffff",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.go_back_to_stalls
        ).pack(side="left")

        self.title_label = tk.Label(
            header,
            text="Carnival POS",
            font=("Helvetica", 18, "bold"),
            bg="#ffffff",
            fg="#0f172a"
        )
        self.title_label.pack(side="left", padx=15)

        self.type_badge = tk.Label(
            header,
            text="",
            font=("Helvetica", 10, "bold"),
            bg="#e0e7ff",
            fg="#3730a3",
            padx=10,
            pady=3
        )
        self.type_badge.pack(side="left")

        tk.Button(
            header,
            text="+ Add Menu Item",
            font=("Helvetica", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            highlightbackground="#ffffff",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.open_add_item_dialog
        ).pack(side="right")

        # main area
        workspace = tk.Frame(self, bg="#f8fafc", padx=15, pady=15)
        workspace.pack(fill="both", expand=True)

        # menu items
        left_box = tk.Frame(workspace, bg="#ffffff", relief="solid", bd=1, padx=15, pady=15)
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            left_box,
            text="Menu Catalog",
            font=("Helvetica", 14, "bold"),
            bg="#ffffff",
            fg="#0f172a",
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        self.menu_canvas = tk.Canvas(left_box, bg="#ffffff", highlightthickness=0)
        self.menu_scrollbar = ttk.Scrollbar(left_box, orient="vertical", command=self.menu_canvas.yview)
        self.menu_items_frame = tk.Frame(self.menu_canvas, bg="#ffffff")

        self.menu_items_frame.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all"))
        )
        self.canvas_window = self.menu_canvas.create_window((0, 0), window=self.menu_items_frame, anchor="nw")

        self.menu_canvas.bind(
            "<Configure>",
            lambda e: self.menu_canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.menu_canvas.configure(yscrollcommand=self.menu_scrollbar.set)
        self.menu_canvas.pack(side="left", fill="both", expand=True)
        self.menu_scrollbar.pack(side="right", fill="y")

        # ------------------ RIGHT: CART and TOTAL ------------------
        right_box = tk.Frame(workspace, bg="#ffffff", relief="solid", bd=1, padx=15, pady=15, width=380)
        right_box.pack(side="right", fill="both")
        right_box.pack_propagate(False)

        tk.Label(
            right_box,
            text="Current Cart / Order",
            font=("Helvetica", 14, "bold"),
            bg="#ffffff",
            fg="#0f172a",
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        cart_scroll_container = tk.Frame(right_box, bg="#ffffff")
        cart_scroll_container.pack(fill="both", expand=True)

        self.cart_canvas = tk.Canvas(cart_scroll_container, bg="#ffffff", highlightthickness=0)
        self.cart_scrollbar = ttk.Scrollbar(cart_scroll_container, orient="vertical", command=self.cart_canvas.yview)
        self.cart_items_frame = tk.Frame(self.cart_canvas, bg="#ffffff")

        self.cart_items_frame.bind(
            "<Configure>",
            lambda e: self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
        )
        self.cart_canvas_window = self.cart_canvas.create_window((0, 0), window=self.cart_items_frame, anchor="nw")

        self.cart_canvas.bind(
            "<Configure>",
            lambda e: self.cart_canvas.itemconfig(self.cart_canvas_window, width=e.width)
        )

        self.cart_canvas.configure(yscrollcommand=self.cart_scrollbar.set)
        self.cart_canvas.pack(side="left", fill="both", expand=True)
        self.cart_scrollbar.pack(side="right", fill="y")

        # total and buttons
        summary_box = tk.Frame(right_box, bg="#f8fafc", relief="solid", bd=1, padx=12, pady=12)
        summary_box.pack(fill="x", pady=(10, 0))

        self.total_label = tk.Label(
            summary_box,
            text="Total: KWD 0.000",
            font=("Helvetica", 16, "bold"),
            bg="#f8fafc",
            fg="#16a34a"
        )
        self.total_label.pack(anchor="e", pady=(0, 10))

        btn_row = tk.Frame(summary_box, bg="#f8fafc")
        btn_row.pack(fill="x")

        cancel_btn = tk.Button(
            btn_row,
            text="Cancel",
            font=("Helvetica", 11, "bold"),
            bg="#ef4444",
            fg="#ffffff",
            highlightbackground="#f8fafc",
            cursor="hand2",
            height=2,
            command=self.cancel_order_click
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        checkout_btn = tk.Button(
            btn_row,
            text="Complete Order",
            font=("Helvetica", 11, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            highlightbackground="#f8fafc",
            cursor="hand2",
            height=2,
            command=self.complete_order_click
        )
        checkout_btn.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def on_show(self):
        stall_id = self.controller.current_stall_id
        stall_name = self.controller.current_stall_name
        stall_type = self.controller.current_stall_type

        self.title_label.config(text=stall_name)
        self.type_badge.config(text=stall_type.upper())

        self.load_menu_items(stall_id)
        self.refresh_order_display()

    def go_back_to_stalls(self):
        if backend.cart:
            confirm = messagebox.askyesno(
                "Unfinished Order",
                "You have items in your cart. Returning will clear the active order. Continue?"
            )
            if not confirm:
                return
        backend.clear_order()
        self.controller.show_frame("StallSelectionScreen")

    def load_menu_items(self, stall_id):
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()

        items = backend.get_items(stall_id)

        if not items:
            tk.Label(
                self.menu_items_frame,
                text="No active menu items found.\nClick '+ Add Menu Item' to add food/drink items.",
                font=("Helvetica", 11),
                bg="#ffffff",
                fg="#64748b",
                pady=30
            ).pack(fill="x")
            return

        for item in items:
            item_id = item[0]
            item_name = item[2]
            price = item[3]
            description = item[4] or ""

            card = tk.Frame(self.menu_items_frame, bg="#ffffff", relief="solid", bd=1, padx=12, pady=10)
            card.pack(fill="x", pady=4, padx=2)

            info = tk.Frame(card, bg="#ffffff")
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=item_name, font=("Helvetica", 12, "bold"), bg="#ffffff", fg="#0f172a", anchor="w").pack(fill="x")
            if description:
                tk.Label(info, text=description, font=("Helvetica", 9), bg="#ffffff", fg="#64748b", anchor="w").pack(fill="x")
            tk.Label(info, text=f"KWD {price:.3f}", font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#2563eb", anchor="w").pack(fill="x", pady=(2, 0))

            tk.Button(
                card,
                text="+ Add",
                font=("Helvetica", 11, "bold"),
                bg="#2563eb",
                fg="#ffffff",
                highlightbackground="#ffffff",
                cursor="hand2",
                padx=12,
                pady=5,
                command=lambda i_id=item_id: self.add_item_click(i_id)
            ).pack(side="right", padx=5)

    def add_item_click(self, item_id):
        backend.add_to_order(item_id)
        self.refresh_order_display()

    def remove_item_click(self, item_id):
        backend.remove_from_order(item_id)
        self.refresh_order_display()

    def cancel_order_click(self):
        if not backend.cart:
            return
        if messagebox.askyesno("Cancel Order", "Clear current order?"):
            backend.clear_order()
            self.refresh_order_display()

    def complete_order_click(self):
        if not backend.cart:
            messagebox.showwarning("Empty Cart", "Please add items to cart before completing order.")
            return

        stall_id = self.controller.current_stall_id
        cart_snapshot = dict(backend.cart)
        total_amount = backend.calculate_total()

        try:
            order_id = backend.complete_order(stall_id)
            if order_id:
                self.refresh_order_display()
                ReceiptModal(
                    self,
                    order_id=order_id,
                    stall_name=self.controller.current_stall_name,
                    cart_snapshot=cart_snapshot,
                    total=total_amount
                )
        except Exception as e:
            messagebox.showerror("Order Error", f"Failed to complete order: {e}")

    def refresh_order_display(self):
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()

        if not backend.cart:
            tk.Label(
                self.cart_items_frame,
                text="Cart is empty.\nClick '+ Add' on menu items.",
                font=("Helvetica", 11, "italic"),
                bg="#ffffff",
                fg="#94a3b8",
                pady=25
            ).pack(fill="x")
        else:
            for item_id, quantity in backend.cart.items():
                item = backend.get_item(item_id)
                if not item:
                    continue

                item_name = item[2]
                price = item[3]
                subtotal = price * quantity

                row = tk.Frame(self.cart_items_frame, bg="#ffffff", relief="solid", bd=1, padx=8, pady=6)
                row.pack(fill="x", pady=2)

                info_col = tk.Frame(row, bg="#ffffff")
                info_col.pack(side="left", fill="both", expand=True)

                tk.Label(info_col, text=item_name, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#0f172a", anchor="w").pack(fill="x")
                tk.Label(info_col, text=f"KWD {subtotal:.3f} (@ {price:.3f})", font=("Helvetica", 9), bg="#ffffff", fg="#64748b", anchor="w").pack(fill="x")

                ctrl_col = tk.Frame(row, bg="#ffffff")
                ctrl_col.pack(side="right")

                tk.Button(
                    ctrl_col,
                    text="-",
                    font=("Helvetica", 9, "bold"),
                    bg="#f1f5f9",
                    highlightbackground="#ffffff",
                    width=2,
                    cursor="hand2",
                    command=lambda i_id=item_id: self.remove_item_click(i_id)
                ).pack(side="left", padx=1)

                tk.Label(ctrl_col, text=str(quantity), font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#0f172a", width=3).pack(side="left")

                tk.Button(
                    ctrl_col,
                    text="+",
                    font=("Helvetica", 9, "bold"),
                    bg="#f1f5f9",
                    highlightbackground="#ffffff",
                    width=2,
                    cursor="hand2",
                    command=lambda i_id=item_id: self.add_item_click(i_id)
                ).pack(side="left", padx=1)

        total = backend.calculate_total()
        self.total_label.config(text=f"Total: KWD {total:.3f}")

    def open_add_item_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Menu Item")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.transient(self)
        dialog.grab_set()

        container = tk.Frame(dialog, bg="#ffffff", padx=25, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Add New Menu Item", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=(0, 15))

        tk.Label(container, text="Item Name:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        name_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        name_entry.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(container, text="Price (e.g. 2.500):", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        price_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        price_entry.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(container, text="Description:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        desc_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        desc_entry.pack(fill="x", pady=(2, 15), ipady=3)

        def submit():
            name = name_entry.get().strip()
            price_text = price_entry.get().strip()
            desc = desc_entry.get().strip()

            if not name or not price_text:
                messagebox.showerror("Error", "Name and price are required.", parent=dialog)
                return

            try:
                price = float(price_text)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric price.", parent=dialog)
                return

            try:
                backend.add_item(self.controller.current_stall_id, name, price, desc, "")
                messagebox.showinfo("Success", f"'{name}' added to menu!", parent=dialog)
                dialog.destroy()
                self.load_menu_items(self.controller.current_stall_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item: {e}", parent=dialog)

        tk.Button(
            container,
            text="Save Menu Item",
            font=("Helvetica", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            highlightbackground="#ffffff",
            command=submit
        ).pack(fill="x", pady=10)


class ReceiptModal(tk.Toplevel):
    def __init__(self, parent, order_id, stall_name, cart_snapshot, total):
        super().__init__(parent)
        self.title("Receipt - Order Completed")
        self.geometry("400x480")
        self.resizable(False, False)
        self.configure(bg="#ffffff")
        self.transient(parent)
        self.grab_set()

        container = tk.Frame(self, bg="#ffffff", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="CARNIVAL RECEIPT", font=("Courier", 15, "bold"), bg="#ffffff", fg="#0f172a").pack()
        tk.Label(container, text=stall_name.upper(), font=("Courier", 11), bg="#ffffff", fg="#475569").pack(pady=(2, 4))
        tk.Label(container, text=f"Order Number: #{order_id:04d}", font=("Courier", 10, "bold"), bg="#ffffff", fg="#0f172a").pack()
        tk.Label(container, text="=" * 34, font=("Courier", 10), bg="#ffffff", fg="#94a3b8").pack(pady=4)

        items_box = tk.Frame(container, bg="#ffffff")
        items_box.pack(fill="both", expand=True, pady=5)

        for item_id, quantity in cart_snapshot.items():
            item = backend.get_item(item_id)
            if item:
                name = item[2]
                price = item[3]
                subtotal = price * quantity

                row = tk.Frame(items_box, bg="#ffffff")
                row.pack(fill="x", pady=1)

                tk.Label(row, text=f"{quantity}x {name[:18]}", font=("Courier", 10), bg="#ffffff", fg="#0f172a", anchor="w").pack(side="left")
                tk.Label(row, text=f"KWD {subtotal:.3f}", font=("Courier", 10), bg="#ffffff", fg="#0f172a", anchor="e").pack(side="right")

        tk.Label(container, text="=" * 34, font=("Courier", 10), bg="#ffffff", fg="#94a3b8").pack(pady=4)
        tk.Label(container, text=f"TOTAL PAID: KWD {total:.3f}", font=("Courier", 13, "bold"), bg="#ffffff", fg="#16a34a").pack(pady=6)
        tk.Label(container, text="Thank you for visiting!\nEnjoy the Carnival!", font=("Courier", 9), bg="#ffffff", fg="#64748b", justify="center").pack(pady=(0, 10))

        tk.Button(
            container,
            text="Next Order",
            font=("Helvetica", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            highlightbackground="#ffffff",
            command=self.destroy
        ).pack(fill="x")


if __name__ == "__main__":
    ensure_initial_data()
    app = CarnivalApp()
    app.mainloop()
