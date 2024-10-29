from fellchensammlung.tools.geo import calculate_distance_between_coordinates
from django.test import TestCase


class DistanceTest(TestCase):
    accuracy = 1.05  # 5% off is ok

    def test_calculate_distance_between_coordinates(self):
        coordinates_berlin = (52.50327,13.41238)
        coordinates_stuttgart = (48.77753579028781, 9.185250111016634)
        coordinates_weil_im_dorf = (48.813691653929276, 9.112217733791029)
        coordinates_with_distance = {"berlin_stuttgart": (coordinates_berlin, coordinates_stuttgart, 510),
                                     "stuttgart_berlin": (coordinates_stuttgart, coordinates_berlin, 510),
                                     "stuttgart_weil": (coordinates_stuttgart, coordinates_weil_im_dorf, 6.7),
                                     }
        for key in coordinates_with_distance:
            (a, b, distance) = coordinates_with_distance[key]
            result = calculate_distance_between_coordinates(a, b)
            try:
                self.assertLess(result, distance * self.accuracy)
                self.assertGreater(result, distance / self.accuracy)
            except AssertionError as e:
                print(f"Distance calculation failed. Expected {distance}, got {result}")
                raise e
