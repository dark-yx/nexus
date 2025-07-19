# payments.py
import os
import paypalrestsdk

class PaymentProcessor:
    def __init__(self):
        paypalrestsdk.configure({
            "mode": os.environ.get("PAYPAL_MODE"),  # sandbox or live
            "client_id": os.environ.get("PAYPAL_CLIENT_ID"),
            "client_secret": os.environ.get("PAYPAL_CLIENT_SECRET")
        })

    def create_paypal_transaction(self, amount, package_name, credits):
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{
                "amount": {"total": f"{amount:.2f}", "currency": "USD"},
                "description": f"Purchase {package_name}: {credits} credits"
            }],
            "redirect_urls": {
                "return_url": "http://nexusmetriks.com/payments/success",
                "cancel_url": "http://nexusmetriks.com/payments/cancel"
            }
        })
        if payment.create():
            return payment
        else:
            return None

    def complete_paypal_transaction(self, payment_id, payer_id):
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            return payment.state == "approved"
        else:
            return False