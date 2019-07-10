

class BaseHexField(object):
    """
    Base class with no additional functionality for tiles. Specific tile
    classes should extend this class.

    Hex fields use an axial coordinate system to track the field locations
    (see https://www.redblobgames.com/grids/hexagons/), where two axes are used
    to describe the location of a given gield. In this coordinate system, the
    immediate neighborhood around a given hex field can be represented as:

        (0, -1)   (1, -1)

    (-1, 0)  (0, 0)  (1, 0)

        (-1, 1)   (0, 1)

    Notice that one axis is the horizontal and another is at a 60 degree angle
    to it.
    """
    __neighbor_directions__ = {
        "topleft", "topright", "bottomleft", "bottomright", "left", "right"}

    def __init__(self, *, coords=None, neighbors=None):
        """
        Creates a single hexagonal tile
        :param coords: An iterable of numerical coordinates.
        :param neighbors: A dictionary of other Field objects. Keys indicate
            direction of neighboring field: "topleft", "topright", "left",
            "right", "bottomleft", "bottomright". A value of None indicates
            that there is no neighbor in this direction, e.g. board edge.
        """
        self._coords = coords if coords is not None else []

        try:
            self._neighbors = {
                key: neighbors[key] for key in BaseHexField.__neighbor_directions__} \
                if neighbors is not None else {
                key: None for key in BaseHexField.__neighbor_directions__}
        except KeyError:
            raise ValueError(
                "If not None, 'neighbors' must be a dictionary with all of "
                "the following keys: {}".format(
                    str(BaseHexField.__neighbor_directions__)))

    def get_coords(self):
        return self._coords

    def set_coords(self, coords):
        self._coords = coords

    def get_neighbors(self):
        return self._neighbors

    def set_neighbors(self, neighbors):
        self._neighbors = neighbors

    def get_neighbor(self, direction):
        try:
            return self._neighbors[direction]
        except KeyError:
            raise ValueError("'direction must be one of {}".format(
                str(BaseHexField.__neighbor_directions__)))


class ValueHexField(BaseHexField):

    def __init__(self, *, coords=None, neighbors=None, value=None):
        """
        Extends BaseHexField with an additional value
        :param coords:
        :param neighbors:
        :param value:
        """
        self._value = value if value is not None else None
        super().__init__(coords=coords, neighbors=neighbors)

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class HexBoard(object):
    """
    The board is essentially a graph of connected fields.
    """

    def __init__(self, *, fields):
        """
        Creates a graph of connected fields.

        Boards should only be initialized via class method constructors.

        :param fields: An iterable of Field objects.
        """
        self._fields = fields

    def get_fields(self):
        return self._fields

    def get_field_at(self, *, coords):
        for field in self._fields:
            if field.get_coords() == coords:
                return field

    @classmethod
    def create_superhex_with_concentric_values(cls, *, radius):
        """
        Create a large hexagon of densely connected tiles. The trick to
        generating a dense hexagon is that he sum of the axial coordinates
        cannot be greater than radius or less than -radius. This means that
        when a hexagon is stored as a 2D array, the top left and bottom right
        corners become NULL, e.g. for a hexagon board with a radius of 3, if
        each axial coordinate is represented by an array dimension, we get a
        coordinate matrix of fields like so:

        NULL    NULL     NULL     (0, -3) (1, -3) (2, -3) (3, -3)
        NULL    NULL     (-1, -2) (0, -2) (1, -2) (2, -2) (3, -2)
        NULL    (-2, -1) (-1, -1) (0, -1) (1, -1) (2, -1) (3, -1)
        (-3, 0) (-2,  0) (-1,  0) (0,  0) (1,  0) (2,  0) (3,  0)
        (-3, 1) (-2,  1) (-1,  1) (0,  1) (1,  1) (2,  1) NULL
        (-3, 2) (-2,  2) (-1,  2) (0,  2) (1,  2) NULL    NULL
        (-3, 3) (-2,  3) (-1,  3) (0,  3)  NULL   NULL    NULL

        The value of each field is determined by its position along the radius,
        i.e. fields at the edge have a value of 1 and the value increases by 1
        with each inner layer. The center of a hexagon with a radius of 3 will
        therefore have a value of 4.

        :param radius: An integer indicating the number of fields that the board
            should extend along each axis.
        :return:
        """
        if radius < 1:
            raise ValueError("'radius' must be an integer >= 1")

        # TODO: Refactor to start building board from center and connecting neighbors during the building process

        # Generate matrix
        fields = []
        for ii in range(0, 2*radius+1):
            x = ii - radius
            fields.append([])
            for jj in range(0, 2*radius+1):
                y = jj - radius
                fields[ii].append(
                    None if abs(x + y) <= radius else
                    ValueHexField()
                )


        for x in range(-radius, radius+1):
            fields.append([])
            for y in range(-radius, radius+1):
                if abs(x + y) <= radius:
                    continue


