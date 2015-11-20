from netlib import encoding
from netlib.tutils import raises


def test_identity():
    assert b"string" == encoding.decode("identity", b"string")
    assert b"string" == encoding.encode("identity", b"string")
    with raises(encoding.CodecException):
        assert not encoding.encode("nonexistent", b"string")
    with raises(encoding.CodecException):
        assert not encoding.decode("nonexistent encoding", b"string")


def test_gzip():
    assert b"string" == encoding.decode(
        "gzip",
        encoding.encode(
            "gzip",
            b"string"
        )
    )
    with raises(encoding.CodecException):
        encoding.decode("gzip", b"bogus")


def test_deflate():
    assert b"string" == encoding.decode(
        "deflate",
        encoding.encode(
            "deflate",
            b"string"
        )
    )
    assert b"string" == encoding.decode(
        "deflate",
        encoding.encode(
            "deflate",
            b"string"
        )[2:-4]
    )
    with raises(encoding.CodecException):
        encoding.decode("deflate", b"bogus")
