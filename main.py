import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import backend


# Sample initial data seeding
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


def center_window(window, width, height, parent=None):
    window.update_idletasks()
    if parent:
        p_win = parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent
        p_win.update_idletasks()
        p_x = p_win.winfo_rootx()
        p_y = p_win.winfo_rooty()
        p_w = p_win.winfo_width()
        p_h = p_win.winfo_height()
        if p_w > 1 and p_h > 1:
            x = p_x + (p_w - width) // 2
            y = p_y + (p_h - height) // 2
        else:
            s_w = window.winfo_screenwidth()
            s_h = window.winfo_screenheight()
            x = (s_w - width) // 2
            y = (s_h - height) // 2
    else:
        s_w = window.winfo_screenwidth()
        s_h = window.winfo_screenheight()
        x = (s_w - width) // 2
        y = (s_h - height) // 2
    window.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")


class CarnivalApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Carnival POS System")
        self.geometry("1100x720")
        self.minsize(950, 600)
        center_window(self, 1100, 720)
        self.configure(bg="#f1f5f9")

        # Current stall context
        self.current_stall_id = None
        self.current_stall_name = ""
        self.current_stall_type = ""

        # Screen container
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

        # Stall dropdown
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

        # Password entry
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

        # Password hint
        self.hint_label = tk.Label(
            card,
            text="Default password for Burger Station: burger123",
            font=("Helvetica", 9, "italic"),
            bg="#ffffff",
            fg="#2563eb"
        )
        self.hint_label.pack(fill="x", pady=(0, 18))

        # Open POS terminal button
        login_btn = tk.Button(
            card,
            text="Open POS Terminal",
            font=("Helvetica", 12, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
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
        stall_id, stall_name, stall_type = stall[0], stall[1], stall[2]
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
        center_window(dialog, 400, 350, parent=self)
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.transient(self.winfo_toplevel())
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
            cursor="hand2",
            command=submit
        ).pack(fill="x", pady=10)


class StallPOSScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller
        self.card_photos = []

        # Top header
        header = tk.Frame(self, bg="#ffffff", padx=20, pady=12, relief="solid", bd=1)
        header.pack(fill="x", side="top")

        tk.Button(
            header,
            text="Switch Stall",
            font=("Helvetica", 11, "bold"),
            bg="#f1f5f9",
            fg="#334155",
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

        # Top-right action buttons
        tk.Button(
            header,
            text="+ Add Menu Item",
            font=("Helvetica", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.open_add_item_dialog
        ).pack(side="right")

        tk.Button(
            header,
            text="Sales Report",
            font=("Helvetica", 10, "bold"),
            bg="#0f766e",
            fg="#ffffff",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.open_sales_report_dialog
        ).pack(side="right", padx=(0, 8))

        # Main workspace
        workspace = tk.Frame(self, bg="#f8fafc", padx=15, pady=15)
        workspace.pack(fill="both", expand=True)

        # Left side: Menu items
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

        # Right side: Cart and total
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

        # Total and action buttons
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

        self.card_photos.clear()
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
            image_path = item[5] or ""

            card = tk.Frame(self.menu_items_frame, bg="#ffffff", relief="solid", bd=1, padx=10, pady=10)
            card.pack(fill="x", pady=4, padx=2)

            # Thumbnail image
            card_img = backend.get_card_image(image_path, size=(75, 75))
            if card_img:
                photo = ImageTk.PhotoImage(card_img)
                self.card_photos.append(photo)
                img_lbl = tk.Label(card, image=photo, bg="#ffffff")
                img_lbl.pack(side="left", padx=(0, 12))
            else:
                placeholder = tk.Frame(card, bg="#f1f5f9", width=75, height=75)
                placeholder.pack_propagate(False)
                placeholder.pack(side="left", padx=(0, 12))
                tk.Label(placeholder, text="🍽️", font=("Segoe UI Emoji", 20), bg="#f1f5f9").place(relx=0.5, rely=0.5, anchor="center")

            # Item details
            info = tk.Frame(card, bg="#ffffff")
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=item_name, font=("Helvetica", 12, "bold"), bg="#ffffff", fg="#0f172a", anchor="w").pack(fill="x")
            if description:
                tk.Label(info, text=description, font=("Helvetica", 9), bg="#ffffff", fg="#64748b", anchor="w").pack(fill="x")
            tk.Label(info, text=f"KWD {price:.3f}", font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#2563eb", anchor="w").pack(fill="x", pady=(2, 0))

            # Action buttons
            actions = tk.Frame(card, bg="#ffffff")
            actions.pack(side="right", padx=(5, 0))

            tk.Button(
                actions,
                text="+ Add",
                font=("Helvetica", 10, "bold"),
                bg="#2563eb",
                fg="#ffffff",
                cursor="hand2",
                padx=12,
                pady=3,
                command=lambda i_id=item_id: self.add_item_click(i_id)
            ).pack(side="top", fill="x", pady=(0, 4))

            btn_sub_row = tk.Frame(actions, bg="#ffffff")
            btn_sub_row.pack(side="bottom", fill="x")

            tk.Button(
                btn_sub_row,
                text="Edit",
                font=("Helvetica", 9),
                bg="#f1f5f9",
                fg="#334155",
                cursor="hand2",
                padx=6,
                pady=2,
                command=lambda it=item: self.open_edit_item_dialog(it)
            ).pack(side="left", padx=(0, 3))

            tk.Button(
                btn_sub_row,
                text="Delete",
                font=("Helvetica", 9),
                bg="#fee2e2",
                fg="#dc2626",
                cursor="hand2",
                padx=6,
                pady=2,
                command=lambda i_id=item_id, n=item_name: self.delete_item_click(i_id, n)
            ).pack(side="left")

    def add_item_click(self, item_id):
        backend.add_to_order(item_id)
        self.refresh_order_display()

    def remove_item_click(self, item_id):
        backend.remove_from_order(item_id)
        self.refresh_order_display()

    def delete_item_click(self, item_id, item_name):
        if messagebox.askyesno("Delete Item", f"Are you sure you want to delete '{item_name}' from the menu?"):
            backend.delete_item(item_id)
            if item_id in backend.cart:
                backend.cart.pop(item_id, None)
                self.refresh_order_display()
            self.load_menu_items(self.controller.current_stall_id)

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
                    width=2,
                    cursor="hand2",
                    command=lambda i_id=item_id: self.add_item_click(i_id)
                ).pack(side="left", padx=1)

        total = backend.calculate_total()
        self.total_label.config(text=f"Total: KWD {total:.3f}")

    def open_add_item_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Menu Item")
        center_window(dialog, 420, 420, parent=self)
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        container = tk.Frame(dialog, bg="#ffffff", padx=25, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Add New Menu Item", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=(0, 15))

        tk.Label(container, text="Item Name:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        name_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        name_entry.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(container, text="Price (e.g. 2.500):", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        price_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        price_entry.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(container, text="Description:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        desc_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        desc_entry.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(container, text="Image File (optional):", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        img_row = tk.Frame(container, bg="#ffffff")
        img_row.pack(fill="x", pady=(2, 15))
        img_entry = tk.Entry(img_row, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        img_entry.pack(side="left", fill="x", expand=True, ipady=3)

        def browse_img():
            f = filedialog.askopenfilename(
                parent=dialog,
                title="Select Item Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.webp"), ("All Files", "*.*")]
            )
            if f:
                img_entry.delete(0, tk.END)
                img_entry.insert(0, f)

        tk.Button(img_row, text="Browse...", font=("Helvetica", 9), bg="#f1f5f9", fg="#334155", cursor="hand2", command=browse_img).pack(side="right", padx=(5, 0))

        def submit():
            name = name_entry.get().strip()
            price_text = price_entry.get().strip()
            desc = desc_entry.get().strip()
            img_path = img_entry.get().strip()

            if not name or not price_text:
                messagebox.showerror("Error", "Name and price are required.", parent=dialog)
                return

            try:
                price = float(price_text)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric price.", parent=dialog)
                return

            try:
                backend.add_item(self.controller.current_stall_id, name, price, desc, img_path)
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
            cursor="hand2",
            command=submit
        ).pack(fill="x", pady=5)

    def open_edit_item_dialog(self, item):
        item_id, _, item_name, price, desc, img_path, _ = item
        dialog = tk.Toplevel(self)
        dialog.title("Edit Menu Item")
        center_window(dialog, 420, 420, parent=self)
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        container = tk.Frame(dialog, bg="#ffffff", padx=25, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Edit Menu Item", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=(0, 15))

        tk.Label(container, text="Item Name:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        name_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        name_entry.insert(0, item_name)
        name_entry.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(container, text="Price (e.g. 2.500):", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        price_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        price_entry.insert(0, f"{price:.3f}")
        price_entry.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(container, text="Description:", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        desc_entry = tk.Entry(container, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        desc_entry.insert(0, desc or "")
        desc_entry.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(container, text="Image File (optional):", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#334155", anchor="w").pack(fill="x")
        img_row = tk.Frame(container, bg="#ffffff")
        img_row.pack(fill="x", pady=(2, 15))
        img_entry = tk.Entry(img_row, font=("Helvetica", 11), bg="#ffffff", fg="#000000", bd=1, relief="solid")
        img_entry.insert(0, img_path or "")
        img_entry.pack(side="left", fill="x", expand=True, ipady=3)

        def browse_img():
            f = filedialog.askopenfilename(
                parent=dialog,
                title="Select Item Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.webp"), ("All Files", "*.*")]
            )
            if f:
                img_entry.delete(0, tk.END)
                img_entry.insert(0, f)

        tk.Button(img_row, text="Browse...", font=("Helvetica", 9), bg="#f1f5f9", fg="#334155", cursor="hand2", command=browse_img).pack(side="right", padx=(5, 0))

        def submit():
            name = name_entry.get().strip()
            price_text = price_entry.get().strip()
            desc_val = desc_entry.get().strip()
            img_val = img_entry.get().strip()

            if not name or not price_text:
                messagebox.showerror("Error", "Name and price are required.", parent=dialog)
                return

            try:
                new_price = float(price_text)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric price.", parent=dialog)
                return

            try:
                backend.update_item(item_id, name, new_price, desc_val, img_val)
                messagebox.showinfo("Success", f"'{name}' updated successfully!", parent=dialog)
                dialog.destroy()
                self.load_menu_items(self.controller.current_stall_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update item: {e}", parent=dialog)

        tk.Button(
            container,
            text="Save Changes",
            font=("Helvetica", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            cursor="hand2",
            command=submit
        ).pack(fill="x", pady=5)

    def open_sales_report_dialog(self):
        stall_id = self.controller.current_stall_id
        stall_name = self.controller.current_stall_name

        total_orders, total_sales, avg_order = backend.get_sales_report(stall_id)
        best_sellers = backend.get_best_selling_items(stall_id)

        dialog = tk.Toplevel(self)
        dialog.title(f"Sales Report - {stall_name}")
        center_window(dialog, 460, 500, parent=self)
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        container = tk.Frame(dialog, bg="#ffffff", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="📊 SALES REPORT", font=("Helvetica", 15, "bold"), bg="#ffffff", fg="#0f172a").pack()
        tk.Label(container, text=stall_name.upper(), font=("Helvetica", 11), bg="#ffffff", fg="#64748b").pack(pady=(2, 12))

        # Stats cards
        stats_box = tk.Frame(container, bg="#f8fafc", relief="solid", bd=1, padx=12, pady=10)
        stats_box.pack(fill="x", pady=(0, 15))

        stat_row = tk.Frame(stats_box, bg="#f8fafc")
        stat_row.pack(fill="x")

        # Total Orders
        c1 = tk.Frame(stat_row, bg="#f8fafc")
        c1.pack(side="left", fill="both", expand=True)
        tk.Label(c1, text="Orders", font=("Helvetica", 9), bg="#f8fafc", fg="#64748b").pack()
        tk.Label(c1, text=str(total_orders), font=("Helvetica", 14, "bold"), bg="#f8fafc", fg="#0f172a").pack()

        # Total Revenue
        c2 = tk.Frame(stat_row, bg="#f8fafc")
        c2.pack(side="left", fill="both", expand=True)
        tk.Label(c2, text="Revenue", font=("Helvetica", 9), bg="#f8fafc", fg="#64748b").pack()
        tk.Label(c2, text=f"KWD {total_sales:.3f}", font=("Helvetica", 14, "bold"), bg="#f8fafc", fg="#16a34a").pack()

        # Avg Order
        c3 = tk.Frame(stat_row, bg="#f8fafc")
        c3.pack(side="left", fill="both", expand=True)
        tk.Label(c3, text="Avg Order", font=("Helvetica", 9), bg="#f8fafc", fg="#64748b").pack()
        tk.Label(c3, text=f"KWD {avg_order:.3f}", font=("Helvetica", 14, "bold"), bg="#f8fafc", fg="#2563eb").pack()

        # Best sellers
        tk.Label(container, text="Top Selling Items", font=("Helvetica", 12, "bold"), bg="#ffffff", fg="#0f172a", anchor="w").pack(fill="x", pady=(5, 5))

        list_box = tk.Frame(container, bg="#ffffff", relief="solid", bd=1, padx=10, pady=8)
        list_box.pack(fill="both", expand=True, pady=(0, 15))

        if not best_sellers:
            tk.Label(list_box, text="No orders recorded for this stall yet.", font=("Helvetica", 10, "italic"), bg="#ffffff", fg="#94a3b8", pady=25).pack()
        else:
            hdr = tk.Frame(list_box, bg="#ffffff")
            hdr.pack(fill="x", pady=(0, 4))
            tk.Label(hdr, text="Item", font=("Helvetica", 9, "bold"), bg="#ffffff", fg="#64748b", anchor="w").pack(side="left")
            tk.Label(hdr, text="Qty Sold", font=("Helvetica", 9, "bold"), bg="#ffffff", fg="#64748b", anchor="e").pack(side="right")
            ttk.Separator(list_box, orient="horizontal").pack(fill="x", pady=2)

            for rank, (name, qty) in enumerate(best_sellers, 1):
                row = tk.Frame(list_box, bg="#ffffff")
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{rank}. {name}", font=("Helvetica", 10), bg="#ffffff", fg="#0f172a", anchor="w").pack(side="left")
                tk.Label(row, text=f"{qty} pcs", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#2563eb", anchor="e").pack(side="right")

        tk.Button(
            container,
            text="Close",
            font=("Helvetica", 11, "bold"),
            bg="#f1f5f9",
            fg="#334155",
            cursor="hand2",
            command=dialog.destroy
        ).pack(fill="x")


class ReceiptModal(tk.Toplevel):
    def __init__(self, parent, order_id, stall_name, cart_snapshot, total):
        super().__init__(parent)
        self.title("Receipt - Order Completed")
        center_window(self, 400, 520, parent=parent)
        self.resizable(False, False)
        self.configure(bg="#ffffff")
        self.transient(parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent)
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

        btn_box = tk.Frame(container, bg="#ffffff")
        btn_box.pack(fill="x")

        def download_pdf():
            try:
                pdf_path = backend.download_receipt_pdf(order_id)
                if pdf_path:
                    messagebox.showinfo("Receipt Saved", f"PDF receipt saved successfully!\nLocation: {pdf_path}", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate receipt PDF: {e}", parent=self)

        tk.Button(
            btn_box,
            text="Download PDF Receipt",
            font=("Helvetica", 10, "bold"),
            bg="#0f766e",
            fg="#ffffff",
            cursor="hand2",
            command=download_pdf
        ).pack(fill="x", pady=(0, 5))

        tk.Button(
            btn_box,
            text="Next Order",
            font=("Helvetica", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            cursor="hand2",
            command=self.destroy
        ).pack(fill="x")


if __name__ == "__main__":
    ensure_initial_data()
    app = CarnivalApp()
    app.mainloop()
