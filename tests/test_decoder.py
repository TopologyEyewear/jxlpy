import os

import jxlpy

WIDTH, HEIGHT = 64, 48


def _encode_rgb(pixels):
    enc = jxlpy.JXLPyEncoder(quality=100, size=(WIDTH, HEIGHT), colorspace='RGB', effort=7)
    enc.add_frame(pixels)
    data = enc.get_output()
    enc.close()
    return data


def test_lossless_round_trip():
    pixels = os.urandom(WIDTH * HEIGHT * 3)

    assert jxlpy.JXLPyDecoder(_encode_rgb(pixels)).get_frame() == pixels


def test_decoder_keeps_its_input_alive():
    # libjxl reads the input lazily, so the decoder must not depend on the caller
    # keeping the bytes object around: a temporary is freed right after __init__
    pixels = os.urandom(WIDTH * HEIGHT * 3)
    data = _encode_rgb(pixels)

    for _ in range(30):
        dec = jxlpy.JXLPyDecoder(bytes(bytearray(data)))
        # Reuse the freed memory before libjxl gets to read it
        churn = [bytes(len(data)) for _ in range(200)]

        assert dec.get_info()['xsize'] == WIDTH
        assert dec.get_frame() == pixels
        del churn
