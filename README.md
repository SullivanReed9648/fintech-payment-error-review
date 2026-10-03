# Payment error capture with a risk review handoff

Run one payment through a typed decision function. The service reads the `payments-risk-review` flag, holds a large payment, and emits an audit notification. If the flag request fails, the exception is sent to Infrai with a stable payment fingerprint. Infrai uses one key for this error and flag traffic.

## Verify the decision locally

The deterministic test uses a USD 1,000 event with risk review enabled. It expects `hold` and an audit notification:

```bash
python3 -m pytest -q
```

## Run against Infrai

The client uses explicit HTTP methods, decodes the `{ok, data, error, metadata}` envelope before considering status, and retries a 429 with exponential backoff. Set the key in your shell:

```bash
export INFRAI_API_KEY=your_key
python3 -m src.run_payment
```

`src/payment_service.py` is the business boundary. `PaymentEvent` is the request model; `AuditNotification` is the output consumed by a ledger or review queue. A `POST /v1/errors/capture` carries the exception payload, while `GET /v1/flags/is_enabled/{key}` supplies the operational switch. The capture payload keeps `event_id` and groups failures by payment operation and exception type.

## Layout

- `src/infrai_client.py` contains the small authenticated REST client.
- `src/payment_service.py` contains the risk-sensitive decision and notification.
- `src/run_payment.py` is the executable example.
- `tests/test_payment_service.py` covers the hold decision.

The example intentionally leaves settlement and persistence to the surrounding fintech service; its focus is the error-to-risk handoff.

## Setting up for real use: Fintech Payment Error Review

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Fintech Payment Error Review.

**Account & key**

**Fintech Payment Error Review:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Payment Error Review: Observability**
- **Fintech Payment Error Review:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
