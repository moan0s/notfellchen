from fellchensammlung.tools.geo import calculate_distance_between_coordinates, LocationProxy
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

    def test_e2e_distance(self):
        l_stuttgart = LocationProxy("Stuttgart")
        l_tue = LocationProxy("Tübingen")
        # Should be 30km
        distance_tue_stuttgart = calculate_distance_between_coordinates(l_stuttgart.position, l_tue.position)
        self.assertLess(distance_tue_stuttgart, 50)
        self.assertGreater(distance_tue_stuttgart, 20)


        l_ueberlingen = LocationProxy("Überlingen")
        l_pfullendorf = LocationProxy("Pfullendorf")
        # Should be 18km
        distance_ueberlingen_pfullendorf = calculate_distance_between_coordinates(l_ueberlingen.position, l_pfullendorf.position)
        self.assertLess(distance_ueberlingen_pfullendorf, 21)
        self.assertGreater(distance_ueberlingen_pfullendorf, 15)


