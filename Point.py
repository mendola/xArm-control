import numpy as np
from numpy.linalg import norm
from typing import Optional, Sequence, Tuple


class Point:
    """ Class for holding and converting position information.  """
    __slots__ = ['cartesian', 'cylindrical', 'spherical', 'azimuth', 'polar', 'radius', 'rho', 'x', 'y', 'z']

    def __init__(self, *,
                 cartesian: Optional[Sequence[float]] = None,
                 cylindrical: Optional[Sequence[float]] = None,
                 spherical: Optional[Sequence[float]] = None):
        """
            Initialize a point in space.
        :param cartesian: Sequence(x, y, z)
        :param cylindrical: Sequence(polar_radius, polar_angle, z)
        :param spherical: Sequence(spherical_radius, azimuth, polar_angle)
        """
        assert bool(cartesian) ^ bool(cylindrical) ^ bool(spherical) and \
            (not (bool(cartesian) and bool(cylindrical) and bool(spherical))), \
            f'Must specify only point type:' \
            f'\n  Cartesian: {cartesian}' \
            f'\n  Cylindrical: {cylindrical}' \
            f'\n  Spherical: {spherical}'

        name_value_pairs = (('cartesian', cartesian), ('cylindrical', cylindrical), ('spherical', spherical))
        var_name, coordinate = next((var_name, value) for var_name, value in name_value_pairs if value is not None)
        self.cartesian, self.cylindrical, self.spherical = getattr(self, f'from_{var_name}')(*eval(var_name))
        self.x, self.y, self.z = self.cartesian
        self.radius = self.cylindrical[0]
        self.rho, self.azimuth, self.polar = self.spherical

    def __repr__(self) -> str:
        return (f'Point('
                f'cartesian=({self.x:+.3f}, {self.y:+.3f}, {self.z:+.3f}), '
                f'cylindrical=({self.radius:+.3f}, {self.polar:+.3f}, {self.z:+.3f}), '
                f'spherical=({self.rho:+.3f}, {self.azimuth:+.3f}, {self.polar:+.3f}))')

    def __eq__(self, other) -> bool:  # type: ignore
        cartesian_equal = np.allclose(self.cartesian, other.cartesian)
        cylindrical_equal = np.isclose(self.radius, other.radius)
        spherical_equal = \
            np.isclose(self.rho, other.rho) and \
            np.isclose(self.azimuth, other.azimuth) and \
            np.isclose(self.polar % 360, other.polar % 360)
        return cartesian_equal and cylindrical_equal and spherical_equal

    @staticmethod
    def from_cartesian(x: float, y: float, z: float) -> Tuple[Sequence[float], Sequence[float], Sequence[float]]:
        """ Converts a Cartesian coordinate to Cylindrical and Spherical. """
        spherical_radius = norm((x, y, z))
        polar_radius = norm((x, y))

        polar_angle = np.rad2deg(np.arctan2(y, x)) - 45
        azimuth = 90 - np.rad2deg(np.arctan2(z, polar_radius))

        return (x, y, z), (polar_radius, polar_angle, z), (spherical_radius, azimuth, polar_angle)

    @staticmethod
    def from_cylindrical(polar_radius: float, polar_angle: float, z: float) -> \
            Tuple[Sequence[float], Sequence[float], Sequence[float]]:
        """ Converts a Cylindrical coordinate to Cartesian and Spherical. """
        x = polar_radius * np.cos(np.deg2rad(polar_angle + 45))
        y = polar_radius * np.sin(np.deg2rad(polar_angle + 45))

        spherical_radius = norm((polar_radius, z))
        azimuth = 90 - np.rad2deg(np.arctan2(z, polar_radius))

        return (x, y, z), (polar_radius, polar_angle, z), (spherical_radius, azimuth, polar_angle)

    @staticmethod
    def from_spherical(spherical_radius: float, azimuth: float, polar_angle: float) -> \
            Tuple[Sequence[float], Sequence[float], Sequence[float]]:
        """ Converts a Spherical coordinate to Cartesian and Cylindrical. """
        x = spherical_radius * np.sin(np.deg2rad(azimuth)) * np.cos(np.deg2rad(polar_angle + 45))
        y = spherical_radius * np.sin(np.deg2rad(azimuth)) * np.sin(np.deg2rad(polar_angle + 45))
        z = spherical_radius * np.cos(np.deg2rad(azimuth))
        polar_radius = spherical_radius * np.sin(np.deg2rad(azimuth))

        return (x, y, z), (polar_radius, polar_angle, z), (spherical_radius, azimuth, polar_angle)

    @classmethod
    def cart2cyl(cls, x: float, y: float, z: float) -> Sequence[float]:
        """ Converts Cartesian to Cylindrical """
        return cls.from_cartesian(x, y, z)[1]

    @classmethod
    def cart2sphere(cls, x: float, y: float, z: float) -> Sequence[float]:
        """ Converts Cartesian to Spherical """
        return cls.from_cartesian(x, y, z)[2]

    @classmethod
    def cyl2cart(cls, polar_radius: float, polar_angle: float, z: float) -> Sequence[float]:
        """ Converts Cylindrical to Cartesian """
        return cls.from_cylindrical(polar_radius, polar_angle, z)[0]

    @classmethod
    def cyl2sphere(cls, polar_radius: float, polar_angle: float, z: float) -> Sequence[float]:
        """ Converts Cylindrical to Spherical """
        return cls.from_cylindrical(polar_radius, polar_angle, z)[2]

    @classmethod
    def sphere2cart(cls, spherical_radius: float, azimuth: float, polar_angle: float) -> Sequence[float]:
        """ Converts Spherical to Cartesian """
        return cls.from_spherical(spherical_radius, azimuth, polar_angle)[0]

    @classmethod
    def sphere2cyl(cls, spherical_radius: float, azimuth: float, polar_angle: float) -> Sequence[float]:
        """ Converts Spherical to Cylindrical """
        return cls.from_spherical(spherical_radius, azimuth, polar_angle)[1]
