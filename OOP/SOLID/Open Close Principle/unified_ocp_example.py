# Violation: Payment processor that violates OCP

class PaymentProcessor:
    def process_payment(self, payment_type, amount):
        if payment_type == "credit_card":
            return self._process_credit_card(amount)
        elif payment_type == "paypal":
            return self._process_paypal(amount)
        elif payment_type == "bitcoin":
            return self._process_bitcoin(amount)
        else:
            raise ValueError("Unsupported payment type")
        
    def _process_credit_card(self, amount):
        return f"Processing ${amount} via Credit Card"
    
    def _process_paypal(self, amount):
        return f"Processing ${amount} via PayPal"
    
    def _process_bitcoin(self, amount):
        return f"Processng ${amount} via Bitcoin"
    
# Above violates OCP because the entities i.e. PaymentProcess needs modification if we need to add any payment method.
# Testing burden
# payment logic is tightly couple
# Violation of SRP

#****Adhering to the OCP****
# PaymentProcess following the OCP
from abc import ABC, abstractmethod


class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass

class CreditCardPayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via Credit Card"
    
class PayPalPayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via PayPal"

class BitcoinPayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via Bitcoin"

# The processor is now CLOSED for modification but OPEN for extension
class PaymentProcessor:

    def __init__(self):
        self.payment_methods = {}
    
    def register_payment_method(self, name, method):
        self.payment_methods[name] = method
    
    def process_payment(self, payment_type, amount):
        if payment_type not in self.payment_methods:
            raise ValueError("Unsupported payment type")
        
        payment_method = self.payment_methods[payment_type]
        return payment_method.process(amount)
    

# Usage demonstrating extension without modification
processor = PaymentProcessor()

# Register existing payment methods
processor.register_payment_method("credit_card", CreditCardPayment())
processor.register_payment_method("paypal", PayPalPayment())
processor.register_payment_method("bitcoin", BitcoinPayment())

# Extend: Add new payment method without modifying existing code
class ApplePayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via Apple Pay"
    
processor.register_payment_method("apple_pay", ApplePayment())

# Test the system
print(processor.process_payment("credit_card", 100))
print(processor.process_payment("paypal", 50))
print(processor.process_payment("apple_pay", 75))

# Advance example: Adding Complex behaviour through extension
class EncryptedPayment(PaymentMethod):
    def __init__(self, base_payment):
        self.base_payment = base_payment
    
    def process(self, amount):
        encrypted_result = self._encrypt(self.base_payment.process(amount))
        return f"[ENCRYPTED] {encrypted_result}"
    
    def _encrypt(self, data):
        return f"ENCRYPTED({data})"
    
# Extend functionality without modifying existing classes
encrypted_credit = EncryptedPayment(CreditCardPayment())
processor.register_payment_method("secure_credit", encrypted_credit)

print(processor.process_payment("secure_credit", 200))
