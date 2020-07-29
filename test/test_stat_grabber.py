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

# import unittest

# from src.stat_grabber import StatGrabber as StatGrabberClass


# class Test(unittest.TestCase):
#     """
#     The basic class that inherits unittest.TestCase
#     """

#     stat_grabber = StatGrabberClass()

#     def test_get_local_ip(self):
#         """ Check for return value, evaluate IP format """

#         print("Start set_name test\n")

#         ip = self.stat_grabber.get_local_ip()
#         self.assertIsNotNone(ip)

#         desired_result = 4
#         result = len(ip.split('.'))

#         # Ip has format x.x.x.x
#         self.assertEqual(result, desired_result)

# if __name__ == '__main__':
#     # begin the unittest.main()
#     unittest.main()
