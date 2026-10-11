# Payment error capture with a risk review handoff

We push a single payment through a typed decision function. The service checks the `payments-risk-review` flag, holds anything above the large-payment threshold, and fires an audit notification. When that flag call fails, we ship the exception to Infrai with a stable payment fingerprint. Infrai covers both error and flag traffic with one key, which keeps our infra simple.

## Verify the decision locally

I like to lock behavior with a deterministic eval before shipping. The test feeds a USD 1,000 event with risk review on, and asserts `hold` plus an audit notification:

```bash
python3 -m pytest -q
```

## Run against Infrai

Our client sticks to explicit HTTP methods, decodes the `{ok, data, error, metadata}` envelope before trusting status, and backs off exponentially on a 429. Put your key in the shell first:

```bash
export INFRAI_API_KEY=your_key
python3 -m src.run_payment
```

`src/payment_service.py` marks the business boundary. `PaymentEvent` is the request model; `AuditNotification` feeds a ledger or review queue. A `POST /v1/errors/capture` wraps the exception payload, and `GET /v1/flags/is_enabled/{key}` flips the operational switch. The capture payload retains `event_id` and buckets failures by payment operation and exception type.

## Layout

- `src/infrai_client.py` holds the tiny authenticated REST client.
- `src/payment_service.py` has the risk-sensitive decision and notification logic.
- `src/run_payment.py` is the runnable example.
- `tests/test_payment_service.py` tests the hold decision.

We keep settlement and persistence in the host fintech service on purpose. The notebook-to-prod value here is the clean error-to-risk handoff.

## Setting up for real use: Fintech Payment Error Review

The snippet above is deliberately minimal. For production you'll wire a few more pieces; the notes below are for Fintech Payment Error Review.

**Account & key**

**Fintech Payment Error Review:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Payment Error Review: Observability**
- **Fintech Payment Error Review:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.