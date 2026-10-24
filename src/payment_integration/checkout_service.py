from .payment_provider_factory import PaymentProviderFactory


class CheckoutService:
    def __init__(self, factory: PaymentProviderFactory):
        self._authorizer = factory.create_authorizer()
        self._refunds = factory.create_refund_processor()
        self._webhooks = factory.create_webhook_verifier()

    def authorize_payment(self, amount: float) -> str:
        return self._authorizer.authorize(amount)

    def refund_payment(self, amount: float) -> str:
        return self._refunds.refund(amount)

    def verify_webhook(self, signature: str) -> bool:
        return self._webhooks.verify(signature)
