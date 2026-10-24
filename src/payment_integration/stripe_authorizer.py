from .authorizer import Authorizer

class StripeAuthorizer(Authorizer):
    def authorize(self, amount: float) -> str:
        return f"stripe:authorized:{amount:.2f}"
