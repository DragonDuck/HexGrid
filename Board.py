

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

    __direction_adjustment__ = {
        "topleft":    (0, -1), "topright":    (1, -1),
        "left":       (-1, 0), "right":       (1,  0),
        "bottomleft": (-1, 1), "bottomright": (0,  1)}

    __opposite_direction__ = {
        "topleft":      "bottomright",
        "topright":     "bottomleft",
        "left":         "right",
        "right":        "left",
        "bottomleft":   "topright",
        "bottomright":  "topleft"}

    def __init__(self, *, coords=None, neighbors=None):
        """
        Creates a single hexagonal tile
        :param coords: An iterable of numerical coordinates.
        :param neighbors: A dictionary of other Field objects. Keys indicate
            direction of neighboring field: "topleft", "topright", "left",
            "right", "bottomleft", "bottomright". A value of None indicates
            that there is no neighbor in this direction, e.g. board edge.
            Note that ONLY dictionary entries with one of the direction names
            as keys will be considered. Missing directions will be set to
            NoneType and additional keys will be ignored
        """
        self._coords = coords if coords is not None else []

        if neighbors is not None:
            self._neighbors = {}
            for key in BaseHexField.__neighbor_directions__:
                if key in neighbors.keys():
                    self._neighbors[key] = neighbors[key]
                else:
                    self._neighbors[key] = None
        else:
            self._neighbors = {
                key: None for key in BaseHexField.__neighbor_directions__}

    def __repr__(self):
        return "<Coords: {}>".format(str(self._coords))

    def get_coords(self):
        return self._coords

    def set_coords(self, coords):
        self._coords = coords

    def get_neighbors(self):
        return self._neighbors

    def set_neighbor(self, direction, neighbor):
        if direction in BaseHexField.__neighbor_directions__:
            self._neighbors[direction] = neighbor
        else:
            raise ValueError("'direction' must be one of {}".format(
                str(BaseHexField.__neighbor_directions__)))

    def set_neighbors(self, neighbors):
        for key in neighbors.keys():
            if key in BaseHexField.__neighbor_directions__:
                self._neighbors[key] = neighbors[key]

    def get_neighbor(self, direction):
        try:
            return self._neighbors[direction]
        except KeyError:
            raise ValueError("'direction must be one of {}".format(
                str(BaseHexField.__neighbor_directions__)))

    @staticmethod
    def get_directions():
        return BaseHexField.__neighbor_directions__

    @staticmethod
    def get_direction_adjustment(direction):
        return BaseHexField.__direction_adjustment__[direction]

    @staticmethod
    def get_opposite_direction(direction):
        return BaseHexField.__opposite_direction__[direction]


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

    def __repr__(self):
        return "<Coords: {}, Value: {}>".format(str(self._coords), str(self._value))

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
        with each inner layer. The center of a hexagon with a radius of N will
        therefore have a value of N+1.

        :param radius: An integer indicating the number of fields that the board
            should extend along each axis. For example, a radius of 1 generates
            a board consisting of a center hex field with 6 neighbors.
        :return:
        """
        if radius < 1:
            raise ValueError("'radius' must be an integer >= 1")

        # TODO: Refactor to start building board from center and connecting neighbors during the building process

        # Place center tile at 0, 0 with NULL neighbors
        fields = [ValueHexField(value=radius+1, coords=(0, 0))]

        # Place concentric rings 'radius' times
        for r in range(1, radius+1):
            new_field_ring = []
            # Loop through all existing fields at a boundary, i.e. with NULL
            # neighbors
            for field in fields:
                for direction in ValueHexField.get_directions():
                    if field.get_neighbor(direction=direction) is None:
                        new_coords = tuple(sum(x) for x in zip(
                            field.get_coords(),
                            ValueHexField.get_direction_adjustment(direction)))
                        new_field = ValueHexField(
                            value=radius+1-r, coords=new_coords,
                            neighbors={ValueHexField.get_opposite_direction(
                                direction=direction): field})
                        field.set_neighbor(direction=direction, neighbor=new_field)
                        new_field_ring.append(new_field)

            fields += new_field_ring

        # Go through all fields again and consolidate duplicate entries by
        # combining their neighbors. Because the code generates the board from
        # the center outwards, this ensures that all neighbors are properly
        # connected.
        final_fields = []
        for field in fields:
            coords = field.get_coords()
            existing_field = [f for f in final_fields if f.get_coords() == coords]
            # If no field at those coordinates exist, add it.
            if len(existing_field) == 0:
                final_fields.append(field)
            # Otherwise, update the neigbors
            elif len(existing_field) == 1:
                for direction, neighbor in field.get_neighbors().items():
                    if existing_field[0].get_neighbor(direction) is None:
                        existing_field[0].set_neighbor(
                            direction=direction, neighbor=neighbor)
            # TODO: This is only for testing. Delete after code is tested thoroughly.
            else:
                raise RuntimeError("Catastrophic error during board creation (A01)")

        return cls(fields=final_fields)
