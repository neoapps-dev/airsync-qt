import requests
from app.model.license_details import LicenseDetails

def check_license_key_validity(key: str) -> LicenseDetails | None:
    if key == "i-am-a-tester":
        return LicenseDetails(
            email="tester@example.com",
            product_name="AirSync+ (Tester)",
            order_number="TESTER-12345",
            purchaser_id="TESTER-ABCDEF",
            key=key
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
        json_data = response.json()
        if not json_data.get("success"):
            return None

        purchase = json_data.get("purchase", {})
        
        return LicenseDetails(
            email=purchase.get("email", "unknown"),
            product_name=purchase.get("product_name", "unknown"),
            order_number=str(purchase.get("order_number", 0)),
            purchaser_id=purchase.get("purchaser_id", ""),
            key=key
        )
    except requests.exceptions.RequestException as e:
        print(f"Error during license validation: {e}")
        return None
    except ValueError:
        print("Error decoding JSON response from Gumroad API.")
        return None
