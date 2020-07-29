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

    # Check type
    assert isinstance(result, int)

@pytest.mark.linux
@pytest.mark.mac
def test_get_cpu_load():
    result = stat_grabber.get_cpu_load()
    assert result != None

    # Check type
    assert isinstance(result, float)

    # Percentage between 0.0 and 100.0
    assert (result >= 0.0) and (result <= 100.0)

@pytest.mark.linux
@pytest.mark.mac
def test_get_memory_percentage():
    result = stat_grabber.get_memory_percentage()
    assert result != None

    # Check type
    assert isinstance(result, float)

    # Percentage between 0.0 and 100.0
    assert (result >= 0.0) and (result <= 100.0)

@pytest.mark.linux
@pytest.mark.mac
def test_get_memory_ratio():
    result = stat_grabber.get_memory_ratio()
    assert result != None

    # Check type
    assert isinstance(result, tuple)

    # Tuple of two
    assert len(result) == 2

    # Check type
    assert isinstance(result[0], float)
    assert isinstance(result[1], float)

    # used memory is smaller or equal to total
    assert result[0]<=result[1]

@pytest.mark.linux
@pytest.mark.mac
def test_get_disk_space():
    result = stat_grabber.get_disk_space()
    assert result != None

    # Check type
    assert isinstance(result, str)

    # Non empty
    assert (len(result) > 0)

@pytest.mark.linux
@pytest.mark.mac
def test_get_time():
    import datetime

    result = stat_grabber.get_time()
    assert result != None

    # Check type
    assert isinstance(result, str)

    # Non empty
    assert (len(result) > 0)

    # Check time format
    date_format = '%H:%M'
    try:
        datetime.datetime.strptime(result, date_format)
    except ValueError:
        raise ValueError('Incorrect data format, should be {}'.format(date_format))

# TODO: check_replace_known_client()
