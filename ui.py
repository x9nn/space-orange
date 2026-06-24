from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)

def print_header(text):
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.YELLOW + text.center(60))
    print(Fore.CYAN + "=" * 60)

def print_module_status(module):
    print(Fore.GREEN + f"Модуль {module.id} (площадь {module.area} м2):")
    res_data = [
        ["Вода", module.resources['water']],
        ["Удобрения", module.resources['fertilizer']],
        ["Энергия", module.resources['energy']]
    ]
    print(tabulate(res_data, headers=["Ресурс", "Количество"], tablefmt="simple"))
    if not module.plants:
        print(Fore.YELLOW + "  Растений нет.")
        return
    plant_rows = []
    for p in module.plants:
        if p.health > 70:
            status = "Здоров"
        elif p.health > 30:
            status = "Внимание"
        else:
            status = "Критично"
        plant_rows.append([
            p.name,
            f"{p.age}/{p.growth_days}",
            f"{p.health}%",
            f"{p.harvest} кг",
            status
        ])
    print(tabulate(plant_rows, headers=["Растение", "Возраст", "Здоровье", "Урожай", "Статус"], tablefmt="grid"))

def print_history(simulator, last_n=5):
    print(Fore.MAGENTA + "Последние события:")
    if not simulator.history:
        print("  История пуста.")
        return
    for entry in simulator.history[-last_n:]:
        print(f"  {entry}")