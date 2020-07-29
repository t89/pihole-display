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
