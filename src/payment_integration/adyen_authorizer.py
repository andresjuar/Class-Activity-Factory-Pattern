from .authorizer import Authorizer
    
class AdyenAuthorizer(Authorizer):
    def authorize(self, amount: float) -> str:
        return f"adyen:authorized:{amount:.2f}"

