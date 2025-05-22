import random
from dataclasses import dataclass
from typing import Optional

@dataclass
class SupplyChainMetrics:
    inventory: int = 12
    backorder: int = 0
    fee_backorder: int = 0
    fee_overorder: int = 0
    incoming_shipment: int = 0
    outgoing_shipment: int = 0

class SupplyChainEntity:
    def __init__(self, name: str, upstream: Optional['SupplyChainEntity'] = None):
        self.name = name
        self.upstream = upstream
        self.metrics = SupplyChainMetrics()
    
    def process_order(self, order: int) -> int:
        """Обработка заказа и возврат фактической отгрузки"""
        if self.metrics.inventory >= order + self.metrics.backorder:
            shipped = order + self.metrics.backorder
            self.metrics.inventory -= shipped
            self.metrics.backorder = 0
        else:
            shipped = self.metrics.inventory
            self.metrics.backorder = (order + self.metrics.backorder) - shipped
            self.metrics.inventory = 0
            self.metrics.fee_backorder += self.metrics.backorder * 2  # Штраф $2 за единицу
        
        # Штраф за избыточные запасы
        if self.metrics.inventory > 12:
            self.metrics.fee_overorder += (self.metrics.inventory - 12) * 1  # Штраф $1 за единицу
            self.metrics.inventory = 12
        
        self.metrics.outgoing_shipment = shipped
        return shipped
    
    def receive_shipment(self, quantity: int):
        """Получение поставки от вышестоящего звена"""
        self.metrics.incoming_shipment = quantity
        self.metrics.inventory += quantity

class Factory(SupplyChainEntity):
    def produce(self):
        """Производство на фабрике (автоматическое пополнение)"""
        self.metrics.inventory += random.randint(1,100)  # Производим случайное
        if self.metrics.inventory > 12:
            self.metrics.inventory = 12

class SupplyChainSimulation:
    def __init__(self):
        self.week = 0
        self.factory = Factory("Фабрика")
        self.distributor = SupplyChainEntity("Дистрибьютор", self.factory)
        self.wholesaler = SupplyChainEntity("Оптовик", self.distributor)
        self.retailer = SupplyChainEntity("Ритейлер", self.wholesaler)
    
    def generate_demand(self) -> int:
        """Генерация спроса покупателя"""
        return random.randint(4, 8)
    
    def process_week(self):
        """Обработка одной недели симуляции"""
        self.week += 1
        demand = self.generate_demand()
        
        # Ритейлер
        retailer_shipped = self.retailer.process_order(demand)
        
        # Оптовик
        wholesaler_shipped = self.wholesaler.process_order(self.retailer.metrics.outgoing_shipment)
        
        # Дистрибьютор
        distributor_shipped = self.distributor.process_order(self.wholesaler.metrics.outgoing_shipment)
        
        # Фабрика
        factory_shipped = self.factory.process_order(self.distributor.metrics.outgoing_shipment)
        self.factory.produce()
        
        # Передача поставок вниз по цепочке
        self.distributor.receive_shipment(factory_shipped)
        self.wholesaler.receive_shipment(distributor_shipped)
        self.retailer.receive_shipment(wholesaler_shipped)
        
        self.print_metrics()
    
    def print_metrics(self):
        """Вывод метрик за неделю"""
        print(f"\n--- Неделя {self.week} ---")
        print(f"Спрос покупателя: {self.retailer.metrics.outgoing_shipment}")
        for entity in [self.retailer, self.wholesaler, self.distributor, self.factory]:
            print(f"{entity.name}:")
            print(f"  Запасы: {entity.metrics.inventory}")
            print(f"  Недопоставки: {entity.metrics.backorder}")
            print(f"  Штрафы: ${entity.metrics.fee_backorder + entity.metrics.fee_overorder}")
            print(f"  Получено/Отгружено: {entity.metrics.incoming_shipment}/{entity.metrics.outgoing_shipment}")

# Запуск симуляции на 10 недель
sim = SupplyChainSimulation()
for _ in range(10):
    sim.process_week()