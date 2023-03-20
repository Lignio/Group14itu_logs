""" import pytest
from controller.app.main import getAnomalyList

@pytest.mark.skip(reason="Docker setup for workflows not yet set up, so this test crashes it all.")
def test_getAnomalyList():
    assert len(getAnomalyList()) > 0
 """