from abc import ABC, abstractmethod

from .authorizer import Authorizer
from .refund_processor import RefundProcessor
from .webhook_verifier import WebhookVerifier

class PaymentProviderFactory(ABC):

    @abstractmethod
    def create_authorizer(self) -> Authorizer: ...

    @abstractmethod
    def create_refund_processor(self) -> RefundProcessor: ...

    @abstractmethod
    def create_webhook_verifier(self) -> WebhookVerifier: ...
