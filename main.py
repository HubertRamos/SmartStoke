"""SmartStoke - controle de estoque simples para pequenos negócios."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from inventory import Inventory, InventoryError


BG = "#f4f6f8"
CARD = "#ffffff"
INK = "#182230"
MUTED = "#667085"
ACCENT = "#2563eb"


class SmartStokeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartStoke | Controle de estoque")
        self.geometry("1080x700")
        self.minsize(850, 560)
        self.configure(bg=BG)
        self.inventory = Inventory()
        self._configure_style()
        self._build_header()
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=22, pady=(8, 20))
        self.dashboard_tab = ttk.Frame(self.tabs, padding=18)
        self.products_tab = ttk.Frame(self.tabs, padding=18)
        self.movements_tab = ttk.Frame(self.tabs, padding=18)
        self.reports_tab = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(self.dashboard_tab, text="Visão geral")
        self.tabs.add(self.products_tab, text="Produtos")
        self.tabs.add(self.movements_tab, text="Movimentações")
        self.tabs.add(self.reports_tab, text="Mais vendidos")
        self._build_dashboard()
        self._build_products()
        self._build_movements()
        self._build_reports()
        self.refresh_all()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=INK, font=("TkDefaultFont", 10))
        style.configure("Title.TLabel", font=("TkDefaultFont", 21, "bold"), foreground=INK)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("TButton", padding=(11, 7), font=("TkDefaultFont", 10))
        style.configure("Accent.TButton", background=ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])
        style.configure("Treeview", rowheight=30, font=("TkDefaultFont", 10), background=CARD, fieldbackground=CARD)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"), padding=8)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 10), font=("TkDefaultFont", 10))

    def _build_header(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=26, pady=(22, 8))
        tk.Label(header, text="SmartStoke", bg=BG, fg=INK, font=("TkDefaultFont", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Controle de estoque simples e direto.", bg=BG, fg=MUTED, font=("TkDefaultFont", 10)).pack(anchor="w", pady=(2, 0))

    def _card(self, parent, title, value, subtitle=""):
        frame = tk.Frame(parent, bg=CARD, highlightbackground="#e4e7ec", highlightthickness=1, padx=18, pady=15)
        tk.Label(frame, text=title, bg=CARD, fg=MUTED, font=("TkDefaultFont", 10)).pack(anchor="w")
        value_label = tk.Label(frame, text=value, bg=CARD, fg=INK, font=("TkDefaultFont", 23, "bold"))
        value_label.pack(anchor="w", pady=(7, 2))
        tk.Label(frame, text=subtitle, bg=CARD, fg=MUTED, font=("TkDefaultFont", 9)).pack(anchor="w")
        return frame, value_label

    def _build_dashboard(self):
        ttk.Label(self.dashboard_tab, text="Resumo do estoque", style="Title.TLabel").pack(anchor="w", pady=(0, 16))
        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x")
        self.card_products, self.value_products = self._card(cards, "Produtos cadastrados", "0", "Itens diferentes")
        self.card_units, self.value_units = self._card(cards, "Unidades em estoque", "0", "Quantidade total")
        self.card_value, self.value_value = self._card(cards, "Valor em estoque", "R$ 0,00", "Preço × quantidade")
        for card in (self.card_products, self.card_units, self.card_value):
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        section = ttk.Frame(self.dashboard_tab)
        section.pack(fill="both", expand=True, pady=(24, 0))
        ttk.Label(section, text="Precisam de atenção", font=("TkDefaultFont", 13, "bold")).pack(anchor="w", pady=(0, 10))
        self.low_tree = self._tree(section, ("name", "quantity", "minimum"), ("Produto", "Disponível", "Estoque mínimo"))
        self.low_tree._wrapper.pack(fill="both", expand=True)
        self.low_tree.bind("<Double-1>", lambda _event: self.tabs.select(self.products_tab))

    def _tree(self, parent, columns, headings):
        wrapper = ttk.Frame(parent)
        tree = ttk.Treeview(wrapper, columns=columns, show="headings", selectmode="browse")
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=150, anchor="w")
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        tree._wrapper = wrapper
        return tree

    def _build_products(self):
        top = ttk.Frame(self.products_tab)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="Produtos", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="+ Novo produto", style="Accent.TButton", command=self.add_product_dialog).pack(side="right")
        search_row = ttk.Frame(self.products_tab)
        search_row.pack(fill="x", pady=(0, 10))
        ttk.Label(search_row, text="Buscar").pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        search = ttk.Entry(search_row, textvariable=self.search_var, width=35)
        search.pack(side="left")
        search.bind("<KeyRelease>", lambda _event: self.refresh_products())
        ttk.Button(search_row, text="Editar", command=self.edit_product_dialog).pack(side="right", padx=(6, 0))
        ttk.Button(search_row, text="Excluir", command=self.delete_product).pack(side="right")
        self.products_tree = self._tree(self.products_tab, ("name", "category", "price", "quantity", "minimum"), ("Produto", "Categoria", "Preço", "Quantidade", "Mínimo"))
        self.products_tree._wrapper.pack(fill="both", expand=True)
        self.products_tree.bind("<Double-1>", lambda _event: self.edit_product_dialog())

    def _build_movements(self):
        top = ttk.Frame(self.movements_tab)
        top.pack(fill="x", pady=(0, 14))
        ttk.Label(top, text="Movimentações", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Registrar entrada", style="Accent.TButton", command=lambda: self.movement_dialog("entry")).pack(side="right", padx=(8, 0))
        ttk.Button(top, text="Registrar saída", command=lambda: self.movement_dialog("exit")).pack(side="right")
        self.movements_tree = self._tree(self.movements_tab, ("date", "product", "type", "quantity", "note"), ("Data", "Produto", "Tipo", "Quantidade", "Observação"))
        self.movements_tree._wrapper.pack(fill="both", expand=True)

    def _build_reports(self):
        ttk.Label(self.reports_tab, text="Produtos mais vendidos", style="Title.TLabel").pack(anchor="w", pady=(0, 12))
        self.chart_area = ttk.Frame(self.reports_tab)
        self.chart_area.pack(fill="both", expand=True)

    def _fill_tree(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", iid=str(row["id"]), values=row["values"])

    def refresh_dashboard(self):
        summary = self.inventory.dashboard()
        self.value_products.config(text=str(summary["products"]))
        self.value_units.config(text=str(summary["units"]))
        formatted = f"R$ {summary['stock_value']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.value_value.config(text=formatted)
        rows = [{"id": p["id"], "values": (p["name"], p["quantity"], p["min_stock"])} for p in self.inventory.low_stock_products()]
        self._fill_tree(self.low_tree, rows)

    def refresh_products(self):
        products = self.inventory.list_products(self.search_var.get())
        rows = [{"id": p["id"], "values": (p["name"], p["category"], f"R$ {p['price']:.2f}", p["quantity"], p["min_stock"])} for p in products]
        self._fill_tree(self.products_tree, rows)

    def refresh_movements(self):
        movements = self.inventory.list_movements()
        rows = [{"id": m["id"], "values": (m["created_at"], m["product_name"], "Entrada" if m["movement_type"] == "entry" else "Saída", m["quantity"], m["note"])} for m in movements]
        self._fill_tree(self.movements_tree, rows)

    def refresh_reports(self):
        for child in self.chart_area.winfo_children():
            child.destroy()
        data = self.inventory.best_sellers()
        if not data:
            ttk.Label(self.chart_area, text="Ainda não há saídas registradas para gerar o gráfico.", style="Muted.TLabel").pack(expand=True)
            return
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            figure = Figure(figsize=(8, 4.5), dpi=100)
            axis = figure.add_subplot(111)
            names = [row["product_name"] for row in reversed(data)]
            values = [row["sold"] for row in reversed(data)]
            axis.barh(names, values, color="#3b82f6")
            axis.set_xlabel("Unidades vendidas")
            axis.set_title("Saídas por produto")
            axis.grid(axis="x", alpha=0.2)
            figure.tight_layout()
            canvas = FigureCanvasTkAgg(figure, master=self.chart_area)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except ImportError:
            ttk.Label(self.chart_area, text="Instale as dependências com: pip install -r requirements.txt").pack(expand=True)

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_products()
        self.refresh_movements()
        self.refresh_reports()

    def _selected_product(self):
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showinfo("SmartStoke", "Selecione um produto primeiro.")
            return None
        return self.inventory.get_product(int(selection[0]))

    def add_product_dialog(self):
        self._product_form("Novo produto")

    def edit_product_dialog(self):
        product = self._selected_product()
        if product:
            self._product_form("Editar produto", product)

    def _product_form(self, title, product=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        fields = [
            ("Nome", product["name"] if product else ""),
            ("Categoria", product["category"] if product else ""),
            ("Preço (R$)", str(product["price"]) if product else "0,00"),
            ("Quantidade inicial", str(product["quantity"]) if product else "0"),
            ("Estoque mínimo", str(product["min_stock"]) if product else "0"),
        ]
        variables = []
        for label, value in fields:
            row = ttk.Frame(dialog, padding=(18, 7))
            row.pack(fill="x")
            ttk.Label(row, text=label, width=19).pack(side="left")
            variable = tk.StringVar(value=value)
            ttk.Entry(row, textvariable=variable, width=30).pack(side="right")
            variables.append(variable)
        if product:
            ttk.Label(dialog, text="A quantidade é alterada pela aba Movimentações.", style="Muted.TLabel").pack(anchor="w", padx=18, pady=(0, 4))

        def save():
            try:
                name, category, price, quantity, minimum = [v.get() for v in variables]
                if product:
                    self.inventory.update_product(product["id"], name, category, price, minimum)
                else:
                    self.inventory.add_product(name, category, price, quantity, minimum)
                dialog.destroy()
                self.refresh_all()
            except (InventoryError, ValueError) as exc:
                messagebox.showerror("Não foi possível salvar", str(exc), parent=dialog)

        buttons = ttk.Frame(dialog, padding=18)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Cancelar", command=dialog.destroy).pack(side="right")
        ttk.Button(buttons, text="Salvar", style="Accent.TButton", command=save).pack(side="right", padx=(0, 8))
        dialog.bind("<Return>", lambda _event: save())

    def delete_product(self):
        product = self._selected_product()
        if product and messagebox.askyesno("Excluir produto", f"Excluir '{product['name']}'? O histórico de movimentações será mantido."):
            self.inventory.delete_product(product["id"])
            self.refresh_all()

    def movement_dialog(self, movement_type):
        products = self.inventory.list_products()
        if not products:
            messagebox.showinfo("SmartStoke", "Cadastre um produto antes de registrar movimentações.")
            return
        dialog = tk.Toplevel(self)
        dialog.title("Registrar entrada" if movement_type == "entry" else "Registrar saída")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        ttk.Label(dialog, text="Produto", padding=(18, 10, 18, 3)).pack(anchor="w")
        choices = {f"{p['name']} (estoque: {p['quantity']})": p for p in products}
        selected = tk.StringVar(value=next(iter(choices)))
        ttk.Combobox(dialog, textvariable=selected, values=list(choices), state="readonly", width=38).pack(padx=18, fill="x")
        ttk.Label(dialog, text="Quantidade", padding=(18, 10, 18, 3)).pack(anchor="w")
        quantity = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=quantity, width=41).pack(padx=18, fill="x")
        ttk.Label(dialog, text="Observação (opcional)", padding=(18, 10, 18, 3)).pack(anchor="w")
        note = tk.StringVar()
        ttk.Entry(dialog, textvariable=note, width=41).pack(padx=18, fill="x")

        def save():
            try:
                self.inventory.register_movement(choices[selected.get()]["id"], movement_type, quantity.get(), note.get())
                dialog.destroy()
                self.refresh_all()
            except InventoryError as exc:
                messagebox.showerror("Movimentação não registrada", str(exc), parent=dialog)

        buttons = ttk.Frame(dialog, padding=18)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Cancelar", command=dialog.destroy).pack(side="right")
        ttk.Button(buttons, text="Confirmar", style="Accent.TButton", command=save).pack(side="right", padx=(0, 8))
        dialog.bind("<Return>", lambda _event: save())


if __name__ == "__main__":
    SmartStokeApp().mainloop()
