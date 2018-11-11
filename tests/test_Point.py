import unittest
from numpy.random import random, rand

from Point import Point


class TestPoint(unittest.TestCase):

    def test_assertions(self):
        """ Test that initialization assertions are tested. """
        with self.assertRaises(AssertionError):
            Point()
        with self.assertRaises(TypeError):
            Point((1, 2, 3))
        with self.assertRaises(AssertionError):
            Point(cartesian=(1, 2, 3), cylindrical=(1, 2, 3))
        with self.assertRaises(AssertionError):
            Point(cartesian=(1, 2, 3), spherical=(1, 2, 3))
        with self.assertRaises(AssertionError):
            Point(cylindrical=(1, 2, 3), spherical=(1, 2, 3))
        with self.assertRaises(AssertionError):
            Point(cartesian=(1, 2, 3), cylindrical=(1, 2, 3), spherical=(1, 2, 3))

    def test_equal(self):
        """ Test that equality of points works as expected. """
        # Arrange
        base_point = Point(cartesian=(1, 0, 1))
        epsilon = 1 * (10 ** -16)

        angle_comparison = Point(cylindrical=(1, 675, 1))
        almost_point = Point(cartesian=(1 - epsilon, epsilon, 1 + epsilon))

        # Act & Assert
        self.assertEqual(base_point, angle_comparison)
        self.assertEqual(base_point, almost_point)

    def test_against_self(self):
        """ Test that Point conversions are self consistent. """
        for _ in range(30):
            test_cartesian = tuple((rand(3) * -20) + 10)
            test_cartesian_point = Point(cartesian=test_cartesian)
            test_cylindrical = test_cartesian_point.cylindrical
            test_spherical = test_cartesian_point.spherical

            self.assertEqual(test_cartesian, test_cartesian_point.cartesian)
            self.assertEqual(test_cartesian_point, Point(cylindrical=test_cylindrical))
            self.assertEqual(test_cartesian_point, Point(spherical=test_spherical))

            for expected, test in zip(test_cartesian, Point.cyl2cart(*Point.cart2cyl(*test_cartesian))):
                self.assertAlmostEqual(expected, test)
            for expected, test in zip(test_cartesian, Point.sphere2cart(*Point.cart2sphere(*test_cartesian))):
                self.assertAlmostEqual(expected, test)

            for expected, test in zip(test_cylindrical, Point.cart2cyl(*Point.cyl2cart(*test_cylindrical))):
                self.assertAlmostEqual(expected, test)
            for expected, test in zip(test_cylindrical, Point.sphere2cyl(*Point.cyl2sphere(*test_cylindrical))):
                self.assertAlmostEqual(expected, test)

            for expected, test in zip(test_spherical, Point.cart2sphere(*Point.sphere2cart(*test_spherical))):
                self.assertAlmostEqual(expected, test)
            for expected, test in zip(test_spherical, Point.cyl2sphere(*Point.sphere2cyl(*test_spherical))):
                self.assertAlmostEqual(expected, test)
