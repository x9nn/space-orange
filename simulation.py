from collections import deque
import random

PLANET_EVENTS = {
    "mars": [
        ("solar_flare", "[Солнечная вспышка] +20 энергии", {"energy": 20}),
        ("meteorite", "[Метеоритный дождь] -10 здоровья", {"damage": 10}),
        ("dust_storm", "[Пылевая буря] -5 воды", {"water": -5}),
        (None, "[Спокойный марсианский день]", {}),
    ],
    "venus": [
        ("volcano", "[Извержение вулкана] +30 энергии", {"energy": 30}),
        ("acid_rain", "[Кислотный дождь] -15 здоровья", {"damage": 15}),
        ("pressure_drop", "[Сбой атмосферы] -10 воды", {"water": -10}),
        (None, "[Серный туман]", {}),
    ],
    "europa": [
        ("ice_quake", "[Ледотрясение] -10 здоровья", {"damage": 10}),
        ("thermal_vent", "[Геотермальный разлом] +20 энергии", {"energy": 20}),
        ("power_outage", "[Отказ генератора] -10 энергии", {"energy": -10}),
        (None, "[Тишина подлёдного океана]", {}),
    ],
    "proxima": [
        ("superflare", "[Мега-вспышка] +50 энергии, -15 здоровья", {"energy": 50, "damage": 15}),
        ("asteroid_dust", "[Пылевой хвост] -5 воды", {"water": -5}),
        ("gravity_anomaly", "[Гравитационный сбой] +10 энергии", {"energy": 10}),
        (None, "[Тусклый красный закат]", {}),
    ],
    "titan": [
        ("methane_rain", "[Метановый ливень] +15 воды", {"water": 15}),
        ("haze_storm", "[Смоговый ураган] -10 здоровья", {"damage": 10}),
        ("cryo_eruption", "[Крио-вулкан] +30 энергии", {"energy": 30}),
        (None, "[Туман над озером]", {}),
    ]
}

class Simulator:
    def __init__(self, modules, resource_manager):
        self.modules = modules
        self.resource_manager = resource_manager
        self.day = 0
        self.task_queue = deque()
        self.history = []
        self.planet = "mars"

    def set_planet(self, planet_name):
        if planet_name in PLANET_EVENTS:
            self.planet = planet_name
            self.history.append(f"Планета сменена на {planet_name.upper()}")
            return True
        return False

    def get_available_planets(self):
        return list(PLANET_EVENTS.keys())

    def generate_tasks(self):
        for module in self.modules:
            for plant in module.plants:
                if plant.health < 50:
                    self.task_queue.append(("urgent_water", module, plant))
                if plant.harvest > 0:
                    self.task_queue.append(("harvest", module, plant))

    def run_day(self):
        self.day += 1
        events_list = PLANET_EVENTS.get(self.planet, PLANET_EVENTS["mars"])
        event_name, desc, effects = random.choice(events_list)
        self.history.append(f"День {self.day} [{self.planet.upper()}]: {desc}")

        if "energy" in effects:
            self.resource_manager.add("energy", effects["energy"])
        if "damage" in effects:
            for mod in self.modules:
                for plant in mod.plants:
                    plant.health = max(0, plant.health - effects["damage"])
        if "water" in effects:
            for mod in self.modules:
                mod.resources["water"] = max(0, mod.resources["water"] + effects["water"])

        for module in self.modules:
            module.simulate_day()

        tasks_done = 0
        while self.task_queue and tasks_done < 5:
            task = self.task_queue.popleft()
            if task[0] == "urgent_water":
                module, plant = task[1], task[2]
                if module._take_resource("water", 5):
                    plant.health = min(100, plant.health + 10)
            elif task[0] == "harvest":
                module, plant = task[1], task[2]
                self.history.append(f"Собран урожай {plant.name} в модуле {module.id}")
                plant.harvest = 0
            tasks_done += 1

        self.generate_tasks()

        for module in self.modules:
            for plant in module.plants:
                if plant.health <= 0:
                    self.history.append(f"Растение {plant.name} в модуле {module.id} погибло!")

        # Уведомления о нехватке ресурсов
        for mod in self.modules:
            for res, amount in mod.resources.items():
                if amount < 5:
                    self.history.append(f"⚠️ В модуле {mod.id} критически мало {res} ({amount})")

        # === НОВОЕ: уведомления о критическом здоровье растений ===
        for mod in self.modules:
            for plant in mod.plants:
                if plant.health < 30 and plant.health > 0:
                    self.history.append(f"⚠️ {plant.name} в модуле {mod.id} при смерти! (здоровье {plant.health}%)")