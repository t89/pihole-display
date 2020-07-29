import pytest
from src.stat_grabber import StatGrabber

stat_grabber = StatGrabber()

@pytest.mark.linux
@pytest.mark.requires_network
def test_get_local_ip():
    ip = stat_grabber.get_local_ip()

    assert ip != None

    desired_result = 4
    result = len(ip.split('.'))

    # Ip has format x.x.x.x
    assert result == desired_result

@pytest.mark.linux
@pytest.mark.mac
@pytest.mark.slow
@pytest.mark.sudo
def test_active_network_device_count():
    result = stat_grabber.get_active_network_device_count()
    assert result != None

    # Return value is integer
    assert isinstance(result, int)

@pytest.mark.linux
@pytest.mark.mac
def test_get_cpu_load():
    result = stat_grabber.get_cpu_load()
    assert result != None

    # Return value is integer
    assert isinstance(result, float)

    # Percentage between 0.0 and 100.0
    assert (result >= 0.0) and (result <= 100.0)

@pytest.mark.linux
@pytest.mark.mac
def test_get_memory_percentage():
    result = stat_grabber.get_memory_percentage()
    assert result != None

    # Return value is integer
    assert isinstance(result, float)

    # Percentage between 0.0 and 100.0
    assert (result >= 0.0) and (result <= 100.0)
