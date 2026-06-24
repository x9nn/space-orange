import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style, Window
from PIL import Image, ImageTk
import os
from models import Tomato, Lettuce, Wheat, Module, ResourceManager
from simulation import Simulator

class SpaceOrangeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Космическая оранжерея")
        self.root.geometry("1000x750")
        self.root.minsize(850, 650)
        self.style = Style(theme="darkly")
        self.root.configure(bg=self.style.colors.bg)

        self.images_dir = os.path.join(os.path.dirname(__file__), "images")
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        self.rm = ResourceManager(water=200, fertilizer=100, energy=500)
        self.module1 = Module(1, area=10, max_plants=5, resource_manager=self.rm)
        self.module2 = Module(2, area=15, max_plants=8, resource_manager=self.rm)
        self.module1.add_plant(Tomato(planet="mars"))
        self.module1.add_plant(Lettuce(planet="mars"))
        self.module2.add_plant(Wheat(planet="mars"))
        self.module2.add_plant(Tomato(planet="mars"))
        self.sim = Simulator([self.module1, self.module2], self.rm)
        self.sim.generate_tasks()
        self.current_planet = "mars"

        self.icons = self.load_icons()
        self.planet_images = {}
        self.resource_images = {}
        self.plant_images = {}

        self.create_widgets()
        self.update_status()

    def load_icons(self):
        icons = {}
        icon_files = {
            "status": "status.png", "day": "day.png", "days": "days.png",
            "resources": "resources.png", "plant": "plant.png", "planet": "planet.png",
            "history": "history.png", "exit": "exit.png",
        }
        for name, filename in icon_files.items():
            path = os.path.join(self.images_dir, filename)
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    img = img.resize((24, 24), Image.Resampling.LANCZOS)
                    icons[name] = ImageTk.PhotoImage(img)
                except:
                    icons[name] = self._make_placeholder(name)
            else:
                icons[name] = self._make_placeholder(name)
        return icons

    def _make_placeholder(self, name):
        colors = {
            "status": "#2ECC71", "day": "#3498DB", "days": "#9B59B6",
            "resources": "#F39C12", "plant": "#27AE60", "planet": "#E74C3C",
            "history": "#1ABC9C", "exit": "#E74C3C",
        }
        img = Image.new("RGB", (24, 24), color=colors.get(name, "#95A5A6"))
        return ImageTk.PhotoImage(img)

    def load_image(self, name, size=(48, 48)):
        path = os.path.join(self.images_dir, f"{name}.png")
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except:
                return None
        return None

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        self.header_label = ttk.Label(top_frame, text="🚀 Космическая оранжерея",
                                      font=("Segoe UI", 20, "bold"))
        self.header_label.pack(side=tk.LEFT, padx=10)

        planet_frame = ttk.Frame(top_frame)
        planet_frame.pack(side=tk.RIGHT, padx=10)
        self.planet_icon_label = ttk.Label(planet_frame)
        self.planet_icon_label.pack(side=tk.LEFT, padx=5)
        self.planet_label = ttk.Label(planet_frame, text="МАРС",
                                      font=("Segoe UI", 14, "bold"), foreground="#5DADE2")
        self.planet_label.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X, pady=5)

        style = ttk.Style()
        style.configure("success.Outline.TButton", font=("Segoe UI", 10), padding=6)
        style.configure("info.Outline.TButton", font=("Segoe UI", 10), padding=6)
        style.configure("warning.Outline.TButton", font=("Segoe UI", 10), padding=6)
        style.configure("danger.Outline.TButton", font=("Segoe UI", 10), padding=6)

        row1 = ttk.Frame(btn_frame)
        row1.pack(fill=tk.X, pady=2)
        btn_status = ttk.Button(row1, image=self.icons["status"], text="  Состояние",
                                compound=tk.LEFT, bootstyle="success-outline",
                                command=self.show_status, width=18)
        btn_status.pack(side=tk.LEFT, padx=5)
        btn_day = ttk.Button(row1, image=self.icons["day"], text="  1 день",
                             compound=tk.LEFT, bootstyle="info-outline",
                             command=self.run_one_day, width=18)
        btn_day.pack(side=tk.LEFT, padx=5)
        btn_days = ttk.Button(row1, image=self.icons["days"], text="  5 дней",
                              compound=tk.LEFT, bootstyle="primary-outline",
                              command=self.run_five_days, width=18)
        btn_days.pack(side=tk.LEFT, padx=5)

        row2 = ttk.Frame(btn_frame)
        row2.pack(fill=tk.X, pady=2)
        btn_res = ttk.Button(row2, image=self.icons["resources"], text="  Ресурсы",
                             compound=tk.LEFT, bootstyle="warning-outline",
                             command=self.choose_resource, width=18)
        btn_res.pack(side=tk.LEFT, padx=5)
        btn_plant = ttk.Button(row2, image=self.icons["plant"], text="  Растение",
                               compound=tk.LEFT, bootstyle="success-outline",
                               command=self.choose_plant, width=18)
        btn_plant.pack(side=tk.LEFT, padx=5)
        btn_planet = ttk.Button(row2, image=self.icons["planet"], text="  Планета",
                                compound=tk.LEFT, bootstyle="info-outline",
                                command=self.change_planet, width=18)
        btn_planet.pack(side=tk.LEFT, padx=5)

        row3 = ttk.Frame(btn_frame)
        row3.pack(fill=tk.X, pady=2)
        btn_history = ttk.Button(row3, image=self.icons["history"], text="  История",
                                 compound=tk.LEFT, bootstyle="secondary-outline",
                                 command=self.show_history, width=18)
        btn_history.pack(side=tk.LEFT, padx=5)
        btn_exit = ttk.Button(row3, image=self.icons["exit"], text="  Выход",
                              compound=tk.LEFT, bootstyle="danger-outline",
                              command=self.root.quit, width=18)
        btn_exit.pack(side=tk.LEFT, padx=5)

        table_frame = ttk.LabelFrame(self.root, text="📋 Состояние системы", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(table_frame, columns=("module", "plant", "age", "health", "harvest", "status"),
                                 show="headings", height=12, bootstyle="dark")
        self.tree.heading("module", text="Модуль")
        self.tree.heading("plant", text="Растение")
        self.tree.heading("age", text="Возраст (дн.)")
        self.tree.heading("health", text="Здоровье (%)")
        self.tree.heading("harvest", text="Урожай (кг)")
        self.tree.heading("status", text="Статус")
        self.tree.column("module", width=80, anchor="center")
        self.tree.column("plant", width=120, anchor="center")
        self.tree.column("age", width=100, anchor="center")
        self.tree.column("health", width=100, anchor="center")
        self.tree.column("harvest", width=100, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_status(self):
        self.planet_label.config(text=self.current_planet.upper())
        img = self.load_image(self.current_planet, size=(32, 32))
        if img:
            self.planet_icon_label.config(image=img)
            self.planet_icon_label.image = img
        else:
            self.planet_icon_label.config(image="", text="🪐")

    def clear_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def refresh_table(self):
        self.clear_tree()
        for mod in self.sim.modules:
            if not mod.plants:
                self.tree.insert("", tk.END, values=(f"Модуль {mod.id}", "Нет растений", "", "", "", ""))
            else:
                for plant in mod.plants:
                    status = "✅ Здоров" if plant.health > 70 else "⚠️ Внимание" if plant.health > 30 else "❌ Критично"
                    self.tree.insert("", tk.END, values=(
                        f"Модуль {mod.id}",
                        plant.name,
                        f"{plant.age}/{plant.growth_days}",
                        f"{plant.health}%",
                        f"{plant.harvest} кг",
                        status
                    ))

    def show_status(self):
        self.refresh_table()

    def run_one_day(self):
        self.sim.run_day()
        messagebox.showinfo("День завершён", f"День {self.sim.day} на планете {self.current_planet.upper()}")
        self.refresh_table()
        if self.sim.history:
            last_events = "\n".join(self.sim.history[-3:])
            messagebox.showinfo("Последние события", last_events)

    def run_five_days(self):
        for _ in range(5):
            self.sim.run_day()
        messagebox.showinfo("Авто-режим", f"Запущено 5 дней. День {self.sim.day}")
        self.refresh_table()

    def choose_resource(self):
        res_window = tk.Toplevel(self.root)
        res_window.title("Выбор ресурса")
        res_window.geometry("500x350")
        res_window.resizable(False, False)
        res_window.configure(bg=self.style.colors.bg)
        tk.Label(res_window, text="Выберите ресурс для пополнения:",
                 font=("Segoe UI", 14, "bold"), bg=self.style.colors.bg, fg=self.style.colors.fg).pack(pady=10)
        frame = ttk.Frame(res_window)
        frame.pack(pady=10)
        resources = [("water", "💧 Вода"), ("fertilizer", "🌱 Удобрения"), ("energy", "⚡ Энергия")]
        col = 0
        for key, label in resources:
            img = self.load_image(key, size=(64, 64))
            if img is None:
                btn = ttk.Button(frame, text=label, bootstyle="info-outline",
                                 command=lambda k=key, w=res_window: self.open_slider_window(k, w))
            else:
                self.resource_images[key] = img
                btn = ttk.Button(frame, image=img, text=label, compound=tk.TOP, bootstyle="info-outline",
                                 command=lambda k=key, w=res_window: self.open_slider_window(k, w))
            btn.grid(row=0, column=col, padx=10, pady=10)
            col += 1
        ttk.Button(res_window, text="Отмена", bootstyle="danger-outline",
                   command=res_window.destroy).pack(pady=10)

    def open_slider_window(self, resource_key, parent_window):
        parent_window.destroy()
        slider_window = tk.Toplevel(self.root)
        slider_window.title(f"Сколько {resource_key}?")
        slider_window.geometry("400x200")
        slider_window.resizable(False, False)
        slider_window.configure(bg=self.style.colors.bg)
        tk.Label(slider_window, text=f"Выберите количество {resource_key}:",
                 font=("Segoe UI", 12), bg=self.style.colors.bg, fg=self.style.colors.fg).pack(pady=10)
        amount_var = tk.IntVar(value=10)
        slider = ttk.Scale(slider_window, from_=1, to=100, orient=tk.HORIZONTAL,
                           variable=amount_var, length=300, bootstyle="info")
        slider.pack(pady=10)
        value_label = ttk.Label(slider_window, text="10", font=("Segoe UI", 14, "bold"))
        value_label.pack(pady=5)
        def update_label(val):
            value_label.config(text=str(int(float(val))))
        slider.configure(command=update_label)
        btn_frame = ttk.Frame(slider_window)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Добавить", bootstyle="success",
                   command=lambda: self.confirm_resource(resource_key, amount_var.get(), slider_window)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", bootstyle="danger",
                   command=slider_window.destroy).pack(side=tk.LEFT, padx=10)

    def confirm_resource(self, resource_key, amount, window):
        if amount > 0:
            self.rm.add(resource_key, amount)
            window.destroy()
            messagebox.showinfo("Успех", f"Добавлено {amount} {resource_key}.")
            self.refresh_table()

    def choose_plant(self):
        plant_window = tk.Toplevel(self.root)
        plant_window.title("Выбор растения")
        plant_window.geometry("550x450")
        plant_window.resizable(False, False)
        plant_window.configure(bg=self.style.colors.bg)
        tk.Label(plant_window, text="Выберите тип растения:",
                 font=("Segoe UI", 14, "bold"), bg=self.style.colors.bg, fg=self.style.colors.fg).pack(pady=10)
        frame = ttk.Frame(plant_window)
        frame.pack(pady=10)
        plants = [("tomato", "🍅 Томат"), ("lettuce", "🥬 Салат"), ("wheat", "🌾 Пшеница")]
        col = 0
        for key, label in plants:
            img = self.load_image(key, size=(64, 64))
            if img is None:
                btn = ttk.Button(frame, text=label, bootstyle="success-outline",
                                 command=lambda k=key, w=plant_window: self.select_plant_type(k, w))
            else:
                self.plant_images[key] = img
                btn = ttk.Button(frame, image=img, text=label, compound=tk.TOP, bootstyle="success-outline",
                                 command=lambda k=key, w=plant_window: self.select_plant_type(k, w))
            btn.grid(row=0, column=col, padx=10, pady=10)
            col += 1
        ttk.Button(plant_window, text="Отмена", bootstyle="danger-outline",
                   command=plant_window.destroy).pack(pady=10)

    def select_plant_type(self, plant_key, parent_window):
        parent_window.destroy()
        module_window = tk.Toplevel(self.root)
        module_window.title("Выбор модуля")
        module_window.geometry("400x250")
        module_window.resizable(False, False)
        module_window.configure(bg=self.style.colors.bg)
        tk.Label(module_window, text="В какой модуль добавить?",
                 font=("Segoe UI", 14, "bold"), bg=self.style.colors.bg, fg=self.style.colors.fg).pack(pady=15)
        module_var = tk.IntVar(value=1)
        style = ttk.Style()
        style.configure("Custom.TRadiobutton", font=("Segoe UI", 12), padding=5)
        rb1 = ttk.Radiobutton(module_window, text="📦 Модуль 1", variable=module_var, value=1, bootstyle="info")
        rb1.pack(pady=5)
        rb2 = ttk.Radiobutton(module_window, text="📦 Модуль 2", variable=module_var, value=2, bootstyle="info")
        rb2.pack(pady=5)
        btn_frame = ttk.Frame(module_window)
        btn_frame.pack(pady=20)
        def add_to_module():
            mod_id = module_var.get()
            mod = next(m for m in self.sim.modules if m.id == mod_id)
            if plant_key == "tomato":
                plant = Tomato(planet=self.current_planet)
            elif plant_key == "lettuce":
                plant = Lettuce(planet=self.current_planet)
            elif plant_key == "wheat":
                plant = Wheat(planet=self.current_planet)
            else:
                messagebox.showerror("Ошибка", "Неизвестный тип.")
                return
            if mod.add_plant(plant):
                module_window.destroy()
                messagebox.showinfo("Успех", f"Растение добавлено в модуль {mod_id}.")
                self.refresh_table()
            else:
                messagebox.showerror("Ошибка", "Модуль переполнен.")
        ttk.Button(btn_frame, text="Добавить", bootstyle="success",
                   command=add_to_module).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", bootstyle="danger",
                   command=module_window.destroy).pack(side=tk.LEFT, padx=10)

    def change_planet(self):
        planet_window = tk.Toplevel(self.root)
        planet_window.title("Выбор планеты")
        planet_window.geometry("550x400")
        planet_window.resizable(False, False)
        planet_window.configure(bg=self.style.colors.bg)
        tk.Label(planet_window, text="Выберите планету:",
                 font=("Segoe UI", 14, "bold"), bg=self.style.colors.bg, fg=self.style.colors.fg).pack(pady=10)
        frame = ttk.Frame(planet_window)
        frame.pack(pady=10)
        planets = self.sim.get_available_planets()
        row, col = 0, 0
        for planet in planets:
            img = self.load_image(planet, size=(64, 64))
            if img is None:
                btn = ttk.Button(frame, text=planet.upper(), bootstyle="primary-outline",
                                 command=lambda p=planet, w=planet_window: self.select_planet(p, w))
            else:
                self.planet_images[planet] = img
                btn = ttk.Button(frame, image=img, text=planet.upper(), compound=tk.TOP,
                                 bootstyle="primary-outline",
                                 command=lambda p=planet, w=planet_window: self.select_planet(p, w))
            btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        ttk.Button(planet_window, text="Отмена", bootstyle="danger-outline",
                   command=planet_window.destroy).pack(pady=10)

    def select_planet(self, planet_name, window):
        if self.sim.set_planet(planet_name):
            self.current_planet = planet_name
            self.update_status()
            self.refresh_table()
            window.destroy()
            messagebox.showinfo("Успех", f"Планета сменена на {planet_name.upper()}!")
        else:
            messagebox.showerror("Ошибка", f"Планета '{planet_name}' не найдена.")

    def show_history(self):
        history_text = "\n".join(self.sim.history) if self.sim.history else "История пуста."
        messagebox.showinfo("История событий", history_text)

if __name__ == "__main__":
    root = Window(themename="darkly")
    app = SpaceOrangeGUI(root)
    root.mainloop()