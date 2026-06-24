from abc import ABC

# Глобальный счётчик для уникальных ID растений
_plant_id_counter = 0

def _generate_plant_id():
    global _plant_id_counter
    _plant_id_counter += 1
    return _plant_id_counter


class Plant(ABC):
    def __init__(self, name, water_need, growth_days, planet="", growth_modifier=1.0):
        self.id = _generate_plant_id()          # уникальный ID
        self.name = name
        self.water_need = water_need
        self.growth_days = growth_days
        self.growth_modifier = growth_modifier
        self.age = 0.0
        self.health = 100
        self.harvest = 0
        self.planet = planet
        self.fertilizer_need = 1.0
        self.good_days = 0

    def grow(self, water_given, energy_given, fertilizer_given):
        if water_given >= self.water_need and energy_given >= 10 and fertilizer_given >= self.fertilizer_need:
            self.age += self.growth_modifier
            self.good_days += 1
            self.health = min(100, self.health + 2)
        else:
            self.health = max(0, self.health - 15)
        if self.age >= self.growth_days and self.harvest == 0:
            ratio = self.good_days / self.growth_days
            self.harvest = int(10 * ratio)

    def reset_for_new_cycle(self):
        self.age = 0.0
        self.good_days = 0


class Tomato(Plant):
    def __init__(self, planet="", growth_modifier=1.0):
        super().__init__("Томат", water_need=2, growth_days=10, planet=planet, growth_modifier=growth_modifier)


class Lettuce(Plant):
    def __init__(self, planet="", growth_modifier=1.0):
        super().__init__("Салат", water_need=1, growth_days=5, planet=planet, growth_modifier=growth_modifier)


class Wheat(Plant):
    def __init__(self, planet="", growth_modifier=1.0):
        super().__init__("Пшеница", water_need=0.5, growth_days=15, planet=planet, growth_modifier=growth_modifier)


class Potato(Plant):
    def __init__(self, planet="", growth_modifier=1.0):
        super().__init__("Картофель", water_need=1.5, growth_days=12, planet=planet, growth_modifier=growth_modifier)


class Carrot(Plant):
    def __init__(self, planet="", growth_modifier=1.0):
        super().__init__("Морковь", water_need=0.8, growth_days=8, planet=planet, growth_modifier=growth_modifier)


class ResourceManager:
    def __init__(self, water=100, fertilizer=50, energy=200):
        self.resources = {"water": water, "fertilizer": fertilizer, "energy": energy}

    def consume(self, resource, amount):
        if self.resources.get(resource, 0) >= amount:
            self.resources[resource] -= amount
            return True
        return False

    def add(self, resource, amount):
        self.resources[resource] = self.resources.get(resource, 0) + amount


class Module:
    def __init__(self, module_id, area, max_plants, resource_manager):
        self.id = module_id
        self.area = area
        self.max_plants = max_plants
        self.plants = []
        self.resources = {"water": 50, "fertilizer": 30, "energy": 100}
        self.resource_manager = resource_manager

    def add_plant(self, plant):
        if len(self.plants) < self.max_plants:
            self.plants.append(plant)
            return True
        return False

    def _take_resource(self, res, amount):
        if self.resources.get(res, 0) >= amount:
            self.resources[res] -= amount
            return True
        need = amount - self.resources.get(res, 0)
        if self.resource_manager.consume(res, need):
            self.resources[res] = 0
            return True
        return False

    def simulate_day(self):
        for plant in self.plants:
            water_ok = self._take_resource("water", plant.water_need)
            energy_ok = self._take_resource("energy", 10)
            fertilizer_ok = self._take_resource("fertilizer", plant.fertilizer_need)
            water_given = plant.water_need if water_ok else 0
            energy_given = 10 if energy_ok else 0
            fertilizer_given = plant.fertilizer_need if fertilizer_ok else 0
            plant.grow(water_given, energy_given, fertilizer_given)