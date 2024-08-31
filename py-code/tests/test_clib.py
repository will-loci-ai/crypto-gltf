import secrets

import numpy as np
from py_code.encrypt.adaptive.utils import get_bits, put_bits
from py_code.utils.numpy_utils import array_bit_slice_eq


def test_put_get_inversion():
    """Test that put_bits is the inverse for get_bits if slice is the whole float"""
    for _ in range(100):
        rows = np.random.randint(1, 1000)
        cols = np.random.randint(1, 16)  # range for 3d mesh matrices
        shape = (rows, cols)
        size = shape[0] * shape[1]
        arr = (
            np.random.random_sample((shape[0] * shape[1]))
            .reshape(shape[0], shape[1], order="C")
            .astype(np.float32)
        )
        start = 0
        stop = 32
        buffer = np.zeros((size), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.float32, order="C")

        get_bits(arr, buffer, shape, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, shape, start, stop)
        assert np.array_equal(arr, putarr)


def test_put_get_varied_slice():
    """Test that put_bits inverses get_bits for varied bit slices"""
    for _ in range(100):
        rows = np.random.randint(1, 1000)
        cols = np.random.randint(1, 16)  # range for 3d mesh matrices
        shape = (rows, cols)
        size = shape[0] * shape[1]
        mat = (
            np.random.random_sample((size))
            .reshape(shape[0], shape[1], order="C")
            .astype(np.float32)
        )
        start = np.random.randint(0, 31)
        stop = np.random.randint(start + 1, 32)
        buffer = np.zeros((size), dtype=np.uint32, order="C")
        putarr = np.zeros(shape, dtype=np.float32, order="C")

        get_bits(mat, buffer, shape, start, stop, secrets.randbits(32))
        put_bits(putarr, buffer, shape, start, stop)

        assert array_bit_slice_eq(mat, putarr, start, stop)
