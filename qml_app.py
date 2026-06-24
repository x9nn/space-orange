import sys
import json
import os
import csv
import atexit
from datetime import datetime
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, qInstallMessageHandler, QtMsgType

from models import Tomato, Lettuce, Wheat, Potato, Carrot, Module, ResourceManager
from simulation import Simulator

def myMessageHandler(msgType, context, msg):
    print(f"QML ERROR: {msg}")

# Функция для получения правильного пути к QML-файлу (работает и для .exe)
def get_qml_path():
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent
    return base_path / "qml" / "main.qml"


class Bridge(QObject):
    def __init__(self):
        super().__init__()
        self.rm = ResourceManager(water=200, fertilizer=100, energy=500)
        self.module1 = Module(1, 10, 5, self.rm)
        self.module2 = Module(2, 15, 8, self.rm)
        self.sim = Simulator([self.module1, self.module2], self.rm)
        self.sim.generate_tasks()
        self.sim.planet = "mars"
        self.total_harvest = 0
        self.harvest_auto_message = ""
        self.resource_history = []
        atexit.register(self.saveState)

    def _get_growth_modifier(self, region):
        modifiers = {
            "mars": 1.0,
            "venus": 1.3,
            "europa": 0.7,
            "proxima": 0.9,
            "titan": 0.8
        }
        return modifiers.get(region.lower(), 1.0)

    @Slot()
    def runDay(self):
        self.sim.run_day()
        self._record_resources()
        self.autoHarvest()

    @Slot()
    def runFiveDays(self):
        for _ in range(5):
            self.sim.run_day()
            self._record_resources()
        self.autoHarvest()

    @Slot(int)
    def runNDays(self, n):
        for _ in range(n):
            self.sim.run_day()
            self._record_resources()
        self.autoHarvest()

    def _record_resources(self):
        self.resource_history.append({
            "day": self.sim.day,
            "water": self.rm.resources["water"],
            "fertilizer": self.rm.resources["fertilizer"],
            "energy": self.rm.resources["energy"]
        })

    def autoHarvest(self):
        total = 0
        count = 0
        for mod in self.sim.modules:
            for p in mod.plants:
                if p.planet == self.sim.planet and p.harvest > 0:
                    total += p.harvest
                    count += 1
                    self.sim.history.append(f"Автосбор: {p.name} ({p.harvest} кг) из региона {self.sim.planet}")
                    p.harvest = 0
                    p.reset_for_new_cycle()
        if count > 0:
            self.total_harvest += total
            self.harvest_auto_message = f"🌾 Автосбор: собрано {total} кг с {count} растений"
        else:
            self.harvest_auto_message = ""

    @Slot(result=str)
    def getLastHarvestMessage(self):
        msg = self.harvest_auto_message
        self.harvest_auto_message = ""
        return msg

    @Slot(result=str)
    def getStatus(self):
        lines = []
        for mod in self.sim.modules:
            lines.append(f"Модуль {mod.id} (площадь {mod.area} м²)")
            lines.append(f"  Вода: {mod.resources['water']}  Удобрения: {mod.resources['fertilizer']}  Энергия: {mod.resources['energy']}")
            if not mod.plants:
                lines.append("  Нет растений")
            else:
                for p in mod.plants:
                    status = "Здоров" if p.health > 70 else "Внимание" if p.health > 30 else "Критично"
                    lines.append(f"  {p.name} | возраст {p.age:.1f}/{p.growth_days} | здоровье {p.health}% | урожай {p.harvest} кг | регион {p.planet} | {status}")
            lines.append("")
        return "\n".join(lines)

    @Slot(result=str)
    def getPlantsData(self):
        current = self.sim.planet
        parts = []
        for mod in self.sim.modules:
            for p in mod.plants:
                if p.planet == current:
                    parts.append(f"{p.id},{p.name},{p.health},{p.age},{p.growth_days},{mod.id},{p.harvest},{mod.resources['water']},{mod.resources['fertilizer']},{mod.resources['energy']}")
        return "|".join(parts)

    @Slot(result=str)
    def getResources(self):
        return f"{self.rm.resources['water']},{self.rm.resources['fertilizer']},{self.rm.resources['energy']}"

    @Slot(result=int)
    def getDay(self):
        return self.sim.day

    @Slot(result=str)
    def getStats(self):
        return f"{self.total_harvest},{self.sim.day}"

    @Slot(int, result=int)
    def getModuleCount(self, module_id):
        for mod in self.sim.modules:
            if mod.id == module_id:
                return len(mod.plants)
        return 0

    @Slot(int, result=int)
    def getModuleMax(self, module_id):
        for mod in self.sim.modules:
            if mod.id == module_id:
                return mod.max_plants
        return 0

    @Slot(str, int)
    def addResource(self, resource_type, amount):
        if amount > 0:
            self.rm.add(resource_type, amount)

    @Slot(str, int, str)
    def addPlant(self, plant_type, module_id, region_name):
        module = next((m for m in self.sim.modules if m.id == module_id), None)
        if not module:
            print("Модуль не найден")
            return
        modifier = self._get_growth_modifier(region_name)
        if plant_type == "tomato":
            plant = Tomato(planet=region_name, growth_modifier=modifier)
        elif plant_type == "lettuce":
            plant = Lettuce(planet=region_name, growth_modifier=modifier)
        elif plant_type == "wheat":
            plant = Wheat(planet=region_name, growth_modifier=modifier)
        elif plant_type == "potato":
            plant = Potato(planet=region_name, growth_modifier=modifier)
        elif plant_type == "carrot":
            plant = Carrot(planet=region_name, growth_modifier=modifier)
        else:
            print("Неизвестный тип растения")
            return
        if module.add_plant(plant):
            print(f"Растение {plant.name} добавлено в модуль {module_id} в регион {region_name} (скорость x{modifier})")
        else:
            print("Модуль переполнен")

    @Slot(str)
    def changeRegion(self, region_name):
        self.sim.set_planet(region_name.lower())
        for mod in self.sim.modules:
            mod.resources = {"water": 50, "fertilizer": 30, "energy": 100}
        print(f"[REGION] Смена региона на {region_name}, ресурсы модулей сброшены")

    @Slot(str, int)
    def removePlant(self, plant_name, module_id):
        for mod in self.sim.modules:
            if mod.id == module_id:
                for i, p in enumerate(mod.plants):
                    if p.name == plant_name and p.planet == self.sim.planet:
                        del mod.plants[i]
                        self.sim.history.append(f"Растение {plant_name} удалено из региона {self.sim.planet} из модуля {module_id}")
                        return

    @Slot(str, int)
    def harvestPlant(self, plant_name, module_id):
        for mod in self.sim.modules:
            if mod.id == module_id:
                for p in mod.plants:
                    if p.name == plant_name and p.planet == self.sim.planet and p.harvest > 0:
                        self.total_harvest += p.harvest
                        self.sim.history.append(f"Собран урожай {p.name} ({p.harvest} кг) в регионе {self.sim.planet}")
                        p.harvest = 0
                        p.reset_for_new_cycle()
                        return

    @Slot(result=str)
    def getCurrentRegion(self):
        return self.sim.planet

    @Slot(result=str)
    def getHistory(self):
        if not self.sim.history:
            return "История пуста."
        return "\n".join(self.sim.history[-15:])

    @Slot()
    def saveState(self, filename="save.json"):
        try:
            state = {
                "day": self.sim.day,
                "planet": self.sim.planet,
                "total_harvest": self.total_harvest,
                "resources": self.rm.resources,
                "modules": [],
                "history": self.sim.history,
                "resource_history": self.resource_history
            }
            for mod in self.sim.modules:
                mod_data = {
                    "id": mod.id,
                    "area": mod.area,
                    "max_plants": mod.max_plants,
                    "resources": mod.resources,
                    "plants": []
                }
                for p in mod.plants:
                    plant_data = {
                        "name": p.name,
                        "health": p.health,
                        "age": p.age,
                        "growth_days": p.growth_days,
                        "growth_modifier": p.growth_modifier,
                        "harvest": p.harvest,
                        "planet": p.planet,
                        "fertilizer_need": p.fertilizer_need,
                        "good_days": p.good_days
                    }
                    mod_data["plants"].append(plant_data)
                state["modules"].append(mod_data)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print(f"[SAVE] Сохранено в {filename}")
        except Exception as e:
            print(f"[SAVE] Ошибка: {e}")

    @Slot()
    def loadState(self, filename="save.json"):
        if not os.path.exists(filename):
            print(f"[LOAD] Файл {filename} не найден")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.sim.day = state["day"]
            self.sim.planet = state["planet"]
            self.total_harvest = state["total_harvest"]
            self.rm.resources = state["resources"]
            self.sim.history = state["history"]
            self.resource_history = state.get("resource_history", [])
            for mod in self.sim.modules:
                mod.plants.clear()
                mod.resources = state["modules"][mod.id-1]["resources"]
                for pdata in state["modules"][mod.id-1]["plants"]:
                    if pdata["name"] == "Томат":
                        plant = Tomato(planet=pdata["planet"], growth_modifier=pdata.get("growth_modifier", 1.0))
                    elif pdata["name"] == "Салат":
                        plant = Lettuce(planet=pdata["planet"], growth_modifier=pdata.get("growth_modifier", 1.0))
                    elif pdata["name"] == "Пшеница":
                        plant = Wheat(planet=pdata["planet"], growth_modifier=pdata.get("growth_modifier", 1.0))
                    elif pdata["name"] == "Картофель":
                        plant = Potato(planet=pdata["planet"], growth_modifier=pdata.get("growth_modifier", 1.0))
                    elif pdata["name"] == "Морковь":
                        plant = Carrot(planet=pdata["planet"], growth_modifier=pdata.get("growth_modifier", 1.0))
                    else:
                        continue
                    plant.health = pdata["health"]
                    plant.age = pdata["age"]
                    plant.growth_days = pdata["growth_days"]
                    plant.harvest = pdata["harvest"]
                    plant.fertilizer_need = pdata.get("fertilizer_need", 1.0)
                    plant.good_days = pdata.get("good_days", 0)
                    mod.add_plant(plant)
            print(f"[LOAD] Загружено из {filename}")
        except Exception as e:
            print(f"[LOAD] Ошибка: {e}")

    @Slot(int, str, int)
    def addResourceToModule(self, module_id, resource_type, amount):
        if amount <= 0:
            return
        for mod in self.sim.modules:
            if mod.id == module_id:
                mod.resources[resource_type] = mod.resources.get(resource_type, 0) + amount
                self.sim.history.append(f"Пополнены ресурсы модуля {module_id}: +{amount} {resource_type}")
                print(f"[MODULE] Модуль {module_id}: +{amount} {resource_type}")
                return

    @Slot()
    def exportCSV(self):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"statistics_{timestamp}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["День", "Регион", "Вода", "Удобрения", "Энергия", "Растение", "Здоровье", "Возраст", "Урожай", "Модуль"])
                for mod in self.sim.modules:
                    for p in mod.plants:
                        writer.writerow([
                            self.sim.day,
                            self.sim.planet,
                            self.rm.resources["water"],
                            self.rm.resources["fertilizer"],
                            self.rm.resources["energy"],
                            p.name,
                            p.health,
                            f"{p.age:.1f}",
                            p.harvest,
                            mod.id
                        ])
            print(f"[CSV] Экспортировано в {filename}")
        except Exception as e:
            print(f"[CSV] Ошибка: {e}")

    @Slot(result=str)
    def getResourceHistory(self):
        return json.dumps(self.resource_history)

    @Slot(str, int, str, result=str)
    def getGrowthPrediction(self, plant_type, module_id, region_name):
        module = next((m for m in self.sim.modules if m.id == module_id), None)
        if not module:
            return "❌ Модуль не найден"
        if len(module.plants) >= module.max_plants:
            return "❌ Модуль переполнен"

        params = {
            "tomato": (2, 1.0, 10),
            "lettuce": (1, 1.0, 5),
            "wheat": (0.5, 1.0, 15),
            "potato": (1.5, 1.0, 12),
            "carrot": (0.8, 1.0, 8)
        }
        if plant_type not in params:
            return "❌ Неизвестный тип"
        water_need, fert_need, growth_days = params[plant_type]

        water_available = module.resources["water"] + self.rm.resources["water"] * 0.3
        fertilizer_available = module.resources["fertilizer"] + self.rm.resources["fertilizer"] * 0.3
        energy_available = module.resources["energy"] + self.rm.resources["energy"] * 0.3

        region_risk = {"mars": 0.9, "venus": 0.6, "europa": 0.8, "proxima": 0.7, "titan": 0.7}.get(region_name.lower(), 0.8)

        water_score = min(1, water_available / (water_need * growth_days * 1.5))
        fert_score = min(1, fertilizer_available / (fert_need * growth_days * 1.5))
        energy_score = min(1, energy_available / (10 * growth_days * 1.5))

        chance = (water_score * 0.4 + fert_score * 0.3 + energy_score * 0.3) * region_risk
        chance = max(0, min(1, chance))

        expected_harvest = int(10 * chance)

        if chance >= 0.8:
            icon, status = "🌱", "Высокий шанс"
        elif chance >= 0.4:
            icon, status = "⚠️", "Средний шанс"
        else:
            icon, status = "💀", "Низкий шанс"

        return f"{icon} {status} ({int(chance * 100)}%) → урожай ~{expected_harvest} кг"

    @Slot(result=str)
    def getRegionStats(self):
        stats = {}
        for mod in self.sim.modules:
            for p in mod.plants:
                region = p.planet
                if region not in stats:
                    stats[region] = {"count": 0, "harvest": 0, "total_age": 0.0}
                stats[region]["count"] += 1
                stats[region]["harvest"] += p.harvest
                stats[region]["total_age"] += p.age

        if not stats:
            return "Нет растений для статистики."

        lines = ["Регион     | Растений | Собрано | Средний возраст | Скорость"]
        lines.append("----------|----------|---------|----------------|---------")
        for region, data in stats.items():
            avg_age = data["total_age"] / data["count"] if data["count"] > 0 else 0
            modifier = self._get_growth_modifier(region)
            speed_text = f"x{modifier:.1f}"
            region_str = region.capitalize().ljust(10)
            count_str = str(data["count"]).rjust(6)
            harvest_str = str(data["harvest"]).rjust(7)
            age_str = f"{avg_age:.1f} дн.".rjust(12)
            speed_str = speed_text.rjust(6)
            lines.append(f"{region_str} | {count_str} | {harvest_str} | {age_str} | {speed_str}")
        return "\n".join(lines)


if __name__ == "__main__":
    qInstallMessageHandler(myMessageHandler)
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    bridge = Bridge()
    engine.rootContext().setContextProperty("bridge", bridge)

    qml_path = get_qml_path()
    print(f"Путь к QML: {qml_path}")
    print(f"Файл существует? {qml_path.exists()}")

    engine.load(qml_path)

    if not engine.rootObjects():
        print("ОШИБКА: QML-файл не загружен!")
        sys.exit(-1)

    print("QML загружен успешно")
    sys.exit(app.exec())