import json
from fastapi import HTTPException


class Cart:
    def __init__(self):
        self.items = {}

    def add(self, product_id: int, quantity: int = 1):
        product_id = str(product_id)
        if product_id in self.items:
            self.items[product_id] += quantity
        else:
            self.items[product_id] = quantity
        if self.items[product_id] <= 0:
            del self.items[product_id]

    def get_items_count(self):
        total = 0
        for product_id, quantity in self.items.items():
            total += quantity
        return total

    def update(self, product_id: int, quantity: int):
        product_id = str(product_id)
        if product_id in self.items:
            if quantity <= 0:
                del self.items[product_id]
            self.items[product_id] = quantity
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    def remove(self, product_id: int):
        product_id = str(product_id)
        if product_id in self.items:
            del self.items[product_id]
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    def clear(self):
        self.items.clear()

    def to_json(self):
        return json.dumps(self.items)

    @classmethod
    def from_json(cls, json_str):
        instance = cls()
        instance.items = json.loads(json_str) if json_str else {}
        return instance
