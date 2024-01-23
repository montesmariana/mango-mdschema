"""Test helper functions"""

import unittest
from irods.meta import iRODSMeta
from mango_mdschema.helpers import flatten, flattend_from_avu, flattened_to_avu, unflatten


class TestFlattening(unittest.TestCase):
    """Test flattening and unflattening of dictionaries."""

    def test_flatten(self):
        """Test flattening of dictionaries."""

        # Test case 1: Empty dictionary
        self.assertEqual(list(flatten({})), [])

        # Test case 2: Nested dictionary
        input_dict = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}
        expected_output = [("a.b.c", 1), ("a.b.d", 2), ("a.e", 3), ("f", 4)]
        self.assertEqual(list(flatten(input_dict)), expected_output)

    def test_unflatten(self):
        """Test unflattening of dictionaries."""

        # Test case 1: Empty dictionary
        self.assertEqual(unflatten([]), {})

        # Test case 2: Flattened dictionary
        input_dict = (("a.b.c", 1), ("a.b.d", 2), ("a.e", 3), ("f", 4))
        expected_output = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}
        self.assertEqual(unflatten(input_dict), expected_output)

    def test_idempotence(self):
        """Test that flatten(unflatten(x)) == x for any dictionary x."""

        # Test case 1: Empty dictionary
        self.assertEqual(unflatten(flatten({})), {})

        # Test case 2: Nested dictionary
        input_dict = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}
        self.assertEqual(unflatten(flatten(input_dict)), input_dict)

        # Test case 3: Nested dictionary with simple list
        input_dict = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4, "g": [5, 6, 7]}
        self.assertEqual(unflatten(flatten(input_dict)), input_dict)

        # Test case 4: Nested dictionary with list of dictionaries
        input_dict = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3,
                    "f": 4,
                    "g": 5,
                    "h": 6,
                },
                "i": 7,
            },
            "j": [{"k": 8, "l": 9}, {"m": 10, "n": 11}],
            "o": [12, 13, 14, 15],
            "p": [
                {"q": [{"r": 16}, {"s": 17}], "t": 18},
                {"u": [{"v": 19}, {"w": 20}], "x": 21},
            ],
            "y": {"z": [{"aa": 22}, {"ab": 23}], "ac": 24},
            "ad": None,
        }
        self.assertEqual(unflatten(flatten(input_dict)), input_dict)


class TestAVUFlattening(unittest.TestCase):
    """Test flattening/unflattening to/from AVUs."""

    schema_prefix = "mgs.test"

    def test_flattened_to_avu(self):
        """Test conversion of flattened key/value pairs to AVUs."""

        prefix = self.schema_prefix

        # Test case 1: Empty list
        self.assertEqual(list(map(lambda x: flattened_to_avu(x, prefix), [])), [])

        # Test case 2: List of tuples with simple fields
        input_list = [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
        expected_output = [
            iRODSMeta(name=f"{prefix}.a", value=1, units=""),
            iRODSMeta(name=f"{prefix}.b", value=2, units=""),
            iRODSMeta(name=f"{prefix}.c", value=3, units=""),
            iRODSMeta(name=f"{prefix}.d", value=4, units=""),
        ]
        self.assertEqual(
            list(map(lambda x: flattened_to_avu(x, prefix), input_list)),
            expected_output,
            msg="Simple fields",
        )

        # Test case 3: List of tuples with nested fields
        input_list = [("a.b.c", 1), ("a.b.d", 2), ("a.e", 3), ("f", 4)]
        expected_output = [
            iRODSMeta(name=f"{prefix}.a.b.c", value=1, units=""),
            iRODSMeta(name=f"{prefix}.a.b.d", value=2, units=""),
            iRODSMeta(name=f"{prefix}.a.e", value=3, units=""),
            iRODSMeta(name=f"{prefix}.f", value=4, units=""),
        ]
        self.assertEqual(
            list(map(lambda x: flattened_to_avu(x, prefix), input_list)),
            expected_output,
            msg="Nested fields",
        )

        # Test case 4: List of tuples with nested fields and list indices
        input_list = [
            ("a[0].b.c", 1),
            ("a[1].b.c", 2),
            ("e.f[0]", 3),
            ("e.f[1]", 4),
            ("g.h[0].i", 5),
            ("g.h[1].j", 6),
        ]
        expected_output = [
            iRODSMeta(name=f"{prefix}.a.b.c", value=1, units="1"),
            iRODSMeta(name=f"{prefix}.a.b.c", value=2, units="2"),
            iRODSMeta(name=f"{prefix}.e.f", value=3, units=""),
            iRODSMeta(name=f"{prefix}.e.f", value=4, units=""),
            iRODSMeta(name=f"{prefix}.g.h.i", value=5, units="0.1"),
            iRODSMeta(name=f"{prefix}.g.h.j", value=6, units="0.2"),
        ]
        self.assertEqual(
            list(map(lambda x: flattened_to_avu(x, prefix), input_list)),
            expected_output,
            msg="Nested fields and list indices",
        )

    def test_dict_to_avu(self):
        """Test conversion of nested dictionaries to AVUs."""

        prefix = self.schema_prefix

        input_dict = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3,
                    "f": 4,
                },
                "i": 7,
            },
            "j": [{"k": 8, "l": 9}, {"m": 10, "n": 11}],
            "o": [12, 13],
            "p": [
                {"q": [{"r": 14}, {"r": 15}], "s": 16},
                {"t": [{"u": 17}, {"u": 18}], "v": 19},
            ],
            "w": {"x": [{"y": 20}, {"y": 21}], "z": 22},
        }
        expected_output = [
            iRODSMeta(name=f"{prefix}.a", value=1, units=""),
            iRODSMeta(name=f"{prefix}.b.c", value=2, units=""),
            iRODSMeta(name=f"{prefix}.b.d.e", value=3, units=""),
            iRODSMeta(name=f"{prefix}.b.d.f", value=4, units=""),
            iRODSMeta(name=f"{prefix}.b.i", value=7, units=""),
            iRODSMeta(name=f"{prefix}.j.k", value=8, units="1"),
            iRODSMeta(name=f"{prefix}.j.l", value=9, units="1"),
            iRODSMeta(name=f"{prefix}.j.m", value=10, units="2"),
            iRODSMeta(name=f"{prefix}.j.n", value=11, units="2"),
            iRODSMeta(name=f"{prefix}.o", value=12, units=""),
            iRODSMeta(name=f"{prefix}.o", value=13, units=""),
            iRODSMeta(name=f"{prefix}.p.q.r", value=14, units="1.1"),
            iRODSMeta(name=f"{prefix}.p.q.r", value=15, units="1.2"),
            iRODSMeta(name=f"{prefix}.p.s", value=16, units="1"),
            iRODSMeta(name=f"{prefix}.p.t.u", value=17, units="2.1"),
            iRODSMeta(name=f"{prefix}.p.t.u", value=18, units="2.2"),
            iRODSMeta(name=f"{prefix}.p.v", value=19, units="2"),
            iRODSMeta(name=f"{prefix}.w.x.y", value=20, units="0.1"),
            iRODSMeta(name=f"{prefix}.w.x.y", value=21, units="0.2"),
            iRODSMeta(name=f"{prefix}.w.z", value=22, units=""),
        ]
        self.assertEqual(
            list(map(lambda x: flattened_to_avu(x, prefix), flatten(input_dict))),
            expected_output,
        )

    def test_idempotence(self):
        """Test conversion of nested dictionaries to AVUs and back."""

        prefix = self.schema_prefix

        input_dict = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3,
                    "f": 4,
                    "g": 5,
                    "h": 6,
                },
                "i": 7,
            },
            "j": [{"k": 8, "l": 9}, {"m": 10, "n": 11}],
            "o": [12, 13],
            "p": [
                {"q": [{"r": 14}, {"r": 15}], "s": 16},
                {"t": [{"u": 17}, {"u": 18}], "v": 19},
            ],
            "w": {"x": [{"y": 20}, {"y": 21}], "z": 22},
        }
        avus = list(map(lambda x: flattened_to_avu(x, prefix), flatten(input_dict)))
        self.assertEqual(
            unflatten(list(map(lambda x: flattend_from_avu(x, prefix), avus))),
            input_dict,
        )


if __name__ == "__main__":
    unittest.main()
