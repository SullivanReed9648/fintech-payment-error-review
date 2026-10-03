import os
from decimal import Decimal

from .infrai_client import InfraiClient
from .payment_service import PaymentEvent, review_payment


def main() -> None:
    if not os.environ.get("INFRAI_API_KEY"):
        raise SystemExit("Set INFRAI_API_KEY before running")
    event = PaymentEvent("pay_demo_001", "cust_42", Decimal("1250.00"), "USD", "US")
    result = review_payment(event, InfraiClient(), lambda note: print(note))
    print(f"decision={result.decision} event_id={result.event_id}")


if __name__ == "__main__":
    main()
