from dataclasses import dataclass

@dataclass
class LicenseDetails:
    email: str
    product_name: str
    order_number: str
    purchaser_id: str
    key: str