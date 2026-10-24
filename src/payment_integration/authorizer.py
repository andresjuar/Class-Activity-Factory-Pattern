from abc import ABC, abstractmethod


class Authorizer(ABC):
    """Product role: authorizes a payment with a provider."""

    @abstractmethod
    def authorize(self, amount: float) -> str:
        raise NotImplementedError
