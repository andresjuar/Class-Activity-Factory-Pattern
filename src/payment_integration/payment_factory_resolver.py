from .adyen_payment_factory import AdyenPaymentFactory
from .mercado_pago_payment_factory import MercadoPagoPaymentFactory
from .payment_provider_factory import PaymentProviderFactory
from .stripe_payment_factory import StripePaymentFactory

class PaymentFactoryResolver:
 
    def __init__(self, factories: dict[str, PaymentProviderFactory] | None = None):
        self._factories = factories if factories is not None else {
            "stripe": StripePaymentFactory(),
            "adyen": AdyenPaymentFactory(),
            "mercado_pago": MercadoPagoPaymentFactory(),
        }

    def resolve(self, provider: str) -> PaymentProviderFactory:
        try:
            return self._factories[provider]
        except KeyError:
            raise ValueError(f"Unsupported provider: {provider}") from None
