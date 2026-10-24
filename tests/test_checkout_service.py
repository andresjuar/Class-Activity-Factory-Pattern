from unittest.mock import create_autospec

import pytest

from payment_integration.adyen_payment_factory import AdyenPaymentFactory
from payment_integration.authorizer import Authorizer
from payment_integration.checkout_service import CheckoutService
from payment_integration.mercado_pago_payment_factory import MercadoPagoPaymentFactory
from payment_integration.payment_factory_resolver import PaymentFactoryResolver
from payment_integration.payment_provider_factory import PaymentProviderFactory
from payment_integration.refund_processor import RefundProcessor
from payment_integration.stripe_payment_factory import StripePaymentFactory
from payment_integration.webhook_verifier import WebhookVerifier


# --- Original tests, adapted to inject a factory ---------------------------


def test_stripe_family_is_selected_together():
    checkout = CheckoutService(StripePaymentFactory())

    assert checkout.authorize_payment(125.50) == "stripe:authorized:125.50"
    assert checkout.refund_payment(25.00) == "stripe:refunded:25.00"
    assert checkout.verify_webhook("stripe-valid") is True
    assert checkout.verify_webhook("adyen-valid") is False


def test_adyen_family_is_selected_together():
    checkout = CheckoutService(AdyenPaymentFactory())

    assert checkout.authorize_payment(125.50) == "adyen:authorized:125.50"
    assert checkout.refund_payment(25.00) == "adyen:refunded:25.00"
    assert checkout.verify_webhook("adyen-valid") is True
    assert checkout.verify_webhook("stripe-valid") is False


def test_mercado_pago_family_is_selected_together():
    checkout = CheckoutService(MercadoPagoPaymentFactory())

    assert checkout.authorize_payment(125.50) == "mercado_pago:authorized:125.50"
    assert checkout.refund_payment(25.00) == "mercado_pago:refunded:25.00"
    assert checkout.verify_webhook("mercado-pago-valid") is True
    assert checkout.verify_webhook("stripe-valid") is False


def test_unsupported_provider_is_rejected():
    with pytest.raises(ValueError):
        PaymentFactoryResolver().resolve("paypal")


# --- New tests ---------------------------------------------------------------

@pytest.mark.parametrize(
    "provider, name, signature, foreign_signatures",
    [
        ("stripe", "stripe", "stripe-valid", ["adyen-valid", "mercado-pago-valid"]),
        ("adyen", "adyen", "adyen-valid", ["stripe-valid", "mercado-pago-valid"]),
        (
            "mercado_pago",
            "mercado_pago",
            "mercado-pago-valid",
            ["stripe-valid", "adyen-valid"],
        ),
    ],
)
def test_resolved_factory_provides_a_complete_family(
    provider, name, signature, foreign_signatures
):
    checkout = CheckoutService(PaymentFactoryResolver().resolve(provider))

    assert checkout.authorize_payment(99.99) == f"{name}:authorized:99.99"
    assert checkout.refund_payment(0.5) == f"{name}:refunded:0.50"
    assert checkout.verify_webhook(signature) is True
    for foreign in foreign_signatures:
        assert checkout.verify_webhook(foreign) is False


@pytest.mark.parametrize(
    "factory",
    [StripePaymentFactory(), AdyenPaymentFactory(), MercadoPagoPaymentFactory()],
)
def test_factory_creates_every_product_role(factory):
    assert isinstance(factory, PaymentProviderFactory)
    assert isinstance(factory.create_authorizer(), Authorizer)
    assert isinstance(factory.create_refund_processor(), RefundProcessor)
    assert isinstance(factory.create_webhook_verifier(), WebhookVerifier)


def test_checkout_delegates_to_an_injected_mock_factory():
    factory = create_autospec(PaymentProviderFactory, instance=True)
    authorizer = factory.create_authorizer.return_value
    refunds = factory.create_refund_processor.return_value
    webhooks = factory.create_webhook_verifier.return_value
    authorizer.authorize.return_value = "mock:authorized"
    refunds.refund.return_value = "mock:refunded"
    webhooks.verify.return_value = False

    checkout = CheckoutService(factory)

    assert checkout.authorize_payment(42.0) == "mock:authorized"
    assert checkout.refund_payment(7.0) == "mock:refunded"
    assert checkout.verify_webhook("tampered") is False

    factory.create_authorizer.assert_called_once_with()
    factory.create_refund_processor.assert_called_once_with()
    factory.create_webhook_verifier.assert_called_once_with()
    authorizer.authorize.assert_called_once_with(42.0)
    refunds.refund.assert_called_once_with(7.0)
    webhooks.verify.assert_called_once_with("tampered")


def test_checkout_creates_the_family_once_and_reuses_it():
    factory = create_autospec(PaymentProviderFactory, instance=True)
    checkout = CheckoutService(factory)

    checkout.authorize_payment(1.0)
    checkout.authorize_payment(2.0)
    checkout.verify_webhook("a")
    checkout.verify_webhook("b")

    factory.create_authorizer.assert_called_once_with()
    factory.create_webhook_verifier.assert_called_once_with()
    assert factory.create_authorizer.return_value.authorize.call_count == 2
    assert factory.create_webhook_verifier.return_value.verify.call_count == 2

    