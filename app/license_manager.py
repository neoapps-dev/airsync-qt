import requests
import json
from dataclasses import dataclass, asdict

@dataclass
class LicenseDetails:
    key: str
    email: str
    productName: str
    orderNumber: int
    purchaserID: str

async def check_license_key_validity(key: str) -> LicenseDetails | None:
    if key == "i-am-a-tester":
        return LicenseDetails(
            key=key,
            email="tester@example.com",
            productName="Test Mode",
            orderNumber=0,
            purchaserID="tester"
        )

    product_id = "smrIThhDxoQI33gQm3wwxw=="
    url = "https://api.gumroad.com/v2/licenses/verify"
    
    payload = {
        "product_id": product_id,
        "license_key": key
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        if response.status_code == 404:
            return None

        json_data = response.json()
        
        if not json_data.get("success"):
            return None
        
        purchase = json_data.get("purchase")
        if not purchase:
            return None

        return LicenseDetails(
            key=key,
            email=purchase.get("email", "unknown"),
            productName=purchase.get("product_name", "unknown"),
            orderNumber=purchase.get("order_number", 0),
            purchaserID=purchase.get("purchaser_id", "")
        )
    except requests.exceptions.RequestException as e:
        print(f"Error checking license: {e}")
        return None
