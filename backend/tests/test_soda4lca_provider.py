import httpx
from httpx import MockTransport, Request, Response

from backend.app.data_providers.soda4lca_provider import Soda4LCAProvider


def _mock_provider(status_code=200, body="", headers=None, exc=None):
    def handler(request: Request) -> Response:
        if exc:
            raise exc
        return Response(status_code=status_code, text=body, headers=headers or {"Content-Type": "application/xml"})

    transport = MockTransport(handler)
    client = httpx.Client(transport=transport)
    return Soda4LCAProvider(base_url="https://example/resource", client=client)


def test_get_process_success():
    xml = """
    <processDataSet>
      <processInformation>
        <dataSetInformation>
          <name>
            <baseName xml:lang=\"en\">Aluminum casting</baseName>
          </name>
          <classification>
            <class level=\"0\">Metals</class>
          </classification>
        </dataSetInformation>
      </processInformation>
      <geography>
        <location>EU</location>
      </geography>
      <flowData>
        <referenceFlow>Reference flow example</referenceFlow>
      </flowData>
    </processDataSet>
    """
    provider = _mock_provider(body=xml)
    candidate = provider.get_process_by_uuid("1234")
    assert candidate is not None
    assert candidate.provider == "soda4lca"
    assert candidate.metadata["location"] == "EU"
    assert candidate.metadata["classification"] == "Metals"


def test_get_process_handles_404():
    provider = _mock_provider(status_code=404, body="Not found")
    candidate = provider.get_process_by_uuid("missing")
    assert candidate is None


def test_get_process_handles_timeout():
    timeout_exc = httpx.ConnectTimeout("timeout")
    provider = _mock_provider(exc=timeout_exc)
    candidate = provider.get_process_by_uuid("slow")
    assert candidate is None
