import os
import paypalrestsdk
import logging
from config import credit_plans

paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "sandbox"),
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

logging.basicConfig(level=logging.INFO)

class PaymentPP:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_payment(self, plan_name, return_url, cancel_url):
        # Obtener el plan de crédito usando el nombre
        plan = credit_plans.get(plan_name)
        if not plan:
            self.logger.error("Plan de crédito no encontrado")
            return None
        
        # Configurar el producto usando la información del plan
        product = {
            "nombre": plan_name,
            "precio": plan["amount"]
        }
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{
                "amount": {
                    "total": f"{product['precio']:.2f}",
                    "currency": "MXN"
                },
                "description": product["nombre"]
            }],
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        })

        if payment.create():
            self.logger.info("Pago creado correctamente")
            return payment
        else:
            self.logger.error(f"Error al crear el pago: {payment.error}")
            return None

    def execute_payment(self, payment_id, payer_id):
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                self.logger.info("Pago ejecutado correctamente")
                return True
            else:
                self.logger.error(f"Error al ejecutar el pago: {payment.error}")
                return False
        except Exception as e:
            self.logger.error(f"Excepción al ejecutar el pago: {e}")
            return False
