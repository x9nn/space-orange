from models import Tomato, Lettuce, Wheat, Module, ResourceManager
from simulation import Simulator
from ui import print_header, print_module_status, print_history

def main():
    rm = ResourceManager(water=200, fertilizer=100, energy=500)
    module1 = Module(1, area=10, max_plants=5, resource_manager=rm)
    module2 = Module(2, area=15, max_plants=8, resource_manager=rm)

    module1.add_plant(Tomato(planet="mars"))
    module1.add_plant(Lettuce(planet="mars"))
    module2.add_plant(Wheat(planet="mars"))
    module2.add_plant(Tomato(planet="mars"))

    sim = Simulator([module1, module2], rm)
    sim.generate_tasks()
    current_planet = "mars"

    while True:
        planets_list = ", ".join(sim.get_available_planets())
        print_header(f"{current_planet.upper()} - КОСМИЧЕСКАЯ ОРАНЖЕРЕЯ")
        print("1. Показать состояние")
        print("2. Выполнить 1 день")
        print("3. Выполнить 5 дней (авто)")
        print("4. Пополнить ресурсы")
        print("5. Добавить растение")
        print("6. История событий")
        print("7. Выход")
        print(f"8. СМЕНИТЬ ПЛАНЕТУ (доступны: {planets_list})")

        choice = input("Выберите действие: ")

        if choice == "1":
            for mod in sim.modules:
                print_module_status(mod)
        elif choice == "2":
            sim.run_day()
            print(f"День {sim.day} завершён на планете {current_planet.upper()}.")
            print_history(sim)
        elif choice == "3":
            for _ in range(5):
                sim.run_day()
            print(f"Запущено 5 дней. Текущий день: {sim.day}")
            print_history(sim)
        elif choice == "4":
            res = input("Какой ресурс? (water/fertilizer/energy): ")
            amount = int(input("Сколько? "))
            rm.add(res, amount)
            print("Ресурсы пополнены.")
        elif choice == "5":
            mod_id = int(input("Номер модуля (1 или 2): "))
            mod = next(m for m in sim.modules if m.id == mod_id)
            plant_type = input("Тип (tomato, lettuce, wheat): ").lower()
            if plant_type == "tomato":
                mod.add_plant(Tomato(planet=current_planet))
            elif plant_type == "lettuce":
                mod.add_plant(Lettuce(planet=current_planet))
            elif plant_type == "wheat":
                mod.add_plant(Wheat(planet=current_planet))
            else:
                print("Неизвестный тип.")
        elif choice == "6":
            print_history(sim, last_n=10)
        elif choice == "7":
            break
        elif choice == "8":
            new_planet = input(f"Введите название планеты ({planets_list}): ").lower().strip()
            if sim.set_planet(new_planet):
                current_planet = new_planet
                print(f"Планета сменена на {new_planet.upper()}!")
            else:
                print(f"Планета '{new_planet}' не найдена. Доступны: {planets_list}")
        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main()