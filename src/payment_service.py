from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Callable

from .infrai_client import InfraiClient, capture_payload


RISK_REVIEW_FLAG = "payments-risk-review"


@dataclass(frozen=True)
class PaymentEvent:
    event_id: str
    customer_id: str
    amount: Decimal
    currency: str
    country: str


@dataclass(frozen=True)
class AuditNotification:
    event_id: str
    decision: str
    reason: str


def review_payment(
    event: PaymentEvent,
    client: InfraiClient,
    notifier: Callable[[AuditNotification], None],
) -> AuditNotification:
    """Hold high-risk payments when the operational flag is enabled."""
    try:
        risk_review = client.is_enabled(RISK_REVIEW_FLAG)
        decision = "hold" if risk_review and event.amount >= Decimal("1000") else "approve"
        reason = "amount threshold with risk review" if decision == "hold" else "standard processing"
    except Exception as error:
        client.capture(capture_payload(event.event_id, error))
        raise
    notification = AuditNotification(event.event_id, decision, reason)
    notifier(notification)
    return notification


def event_dict(event: PaymentEvent) -> dict:
    value = asdict(event)
    value["amount"] = str(value["amount"])
    return value
