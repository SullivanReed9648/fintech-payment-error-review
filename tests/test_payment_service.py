from decimal import Decimal

from src.payment_service import PaymentEvent, review_payment


class FlagClient:
    def is_enabled(self, key):
        assert key == "payments-risk-review"
        return True


def test_large_payment_is_held_and_audited():
    notes = []
    event = PaymentEvent("pay_7", "cust_9", Decimal("1000"), "USD", "US")
    result = review_payment(event, FlagClient(), notes.append)
    assert result.decision == "hold"
    assert result.reason == "amount threshold with risk review"
    assert notes == [result]
