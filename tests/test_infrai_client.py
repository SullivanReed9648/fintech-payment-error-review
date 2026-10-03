from src.infrai_client import InfraiClient


class MissingFlagSession:
    @staticmethod
    def request(method, url, json, headers, timeout):
        assert method == "GET"
        assert url.endswith("/v1/flags/is_enabled/payments-risk-review")
        return Response()


class Response:
    status_code = 404
    headers = {}

    @staticmethod
    def json():
        return {"ok": False, "error": {"code": "FLAG_NOT_FOUND"}}


def test_missing_flag_is_disabled():
    client = InfraiClient(api_key="test", session=MissingFlagSession())
    assert client.is_enabled("payments-risk-review") is False
