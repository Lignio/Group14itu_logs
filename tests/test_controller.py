from controller.app.main import getAnomalyList


def test_getAnomalyList():
    assert len(getAnomalyList()) > 0
