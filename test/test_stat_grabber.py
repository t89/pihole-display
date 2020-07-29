import pytest
from src.stat_grabber import StatGrabber

stat_grabber = StatGrabber()

@pytest.mark.requires_network
@pytest.mark.linux
def test_get_local_ip():
    ip = stat_grabber.get_local_ip()

    assert ip != None

    desired_result = 4
    result = len(ip.split('.'))

    # Ip has format x.x.x.x
    assert result == desired_result

@pytest.mark.sudo
@pytest.mark.slow
@pytest.mark.mac
def test_active_network_device_count():
    result = stat_grabber.get_active_network_device_count()
    assert result != None

    # Return value is integer
    assert isinstance(result, int)
