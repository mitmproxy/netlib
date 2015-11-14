from __future__ import absolute_import, print_function, division
import warnings
import cgi
import six
from .headers import Headers
from .. import encoding, utils

CONTENT_MISSING = 0

if six.PY2:  # pragma: nocover
    _native = lambda x: x
    _always_bytes = lambda x: x
else:
    # While the HTTP head _should_ be ASCII, it's not uncommon for certain headers to be utf-8 encoded.
    _native = lambda x: x.decode("utf-8", "surrogateescape")
    _always_bytes = lambda x: utils.always_bytes(x, "utf-8", "surrogateescape")


class MessageData(object):
    def __init__(self, headers, raw_content):
        if not headers:
            headers = Headers()
        assert isinstance(headers, Headers)
        self.headers = headers

        self.raw_content = raw_content

    def __eq__(self, other):
        if isinstance(other, MessageData):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Message(object):
    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.data == other.data
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def headers(self):
        """
        Message headers object

        Returns:
            netlib.http.Headers
        """
        return self.data.headers

    @headers.setter
    def headers(self, h):
        self.data.headers = h

    @property
    def raw_content(self):
        """
        The raw, unmodified HTTP message body

        See also: :py:attr:`content`, :py:attr:`text`
        """
        return self.data.raw_content

    @raw_content.setter
    def raw_content(self, raw_content):
        self.data.raw_content = raw_content
        if isinstance(raw_content, bytes):
            self.headers["content-length"] = str(len(raw_content))

    @property
    def content(self):
        """
        The (decoded) HTTP message body.
        If the Content-Encoding is invalid, identity encoding is used.

        Decoded contents are not cached, so accessing this attribute repeatedly is relatively expensive.

        See also: :py:attr:`raw_content`, :py:attr:`text`
        """
        ce = self.headers.get("content-encoding")
        if ce:
            try:
                return encoding.decode(ce, self.raw_content)
            except encoding.CodecException:
                pass
        return self.raw_content

    @content.setter
    def content(self, content):
        ce = self.headers.get("content-encoding")
        try:
            self.raw_content = encoding.encode(ce, content)
        except encoding.CodecException:
            self.raw_content = content

    @property
    def http_version(self):
        """
        Version string, e.g. "HTTP/1.1"
        """
        return _native(self.data.http_version)

    @http_version.setter
    def http_version(self, http_version):
        self.data.http_version = _always_bytes(http_version)

    @property
    def timestamp_start(self):
        """
        First byte timestamp
        """
        return self.data.timestamp_start

    @timestamp_start.setter
    def timestamp_start(self, timestamp_start):
        self.data.timestamp_start = timestamp_start

    @property
    def timestamp_end(self):
        """
        Last byte timestamp
        """
        return self.data.timestamp_end

    @timestamp_end.setter
    def timestamp_end(self, timestamp_end):
        self.data.timestamp_end = timestamp_end

    @property
    def charset(self):
        """
        Determine the text encoding from the HTTP Content-Type header.
        Encodings specified in the HTTP body are not considered (yet).

        Caveats:
            This returns the text encoding, which is _not_ the HTTP Content-Encoding.
        """

        content_type = self.headers.get('content-type')
        if not content_type:
            return None

        content_type, params = cgi.parse_header(content_type)
        if 'charset' in params:
            return params['charset'].strip("'\"")
        if 'text' in content_type:
            return 'ISO-8859-1'
        return None

    @property
    def text(self):
        """
        The decoded HTTP message body.

        Decoded contents are not cached, so accessing this attribute repeatedly is relatively expensive.

        See also: :py:attr:`content`, :py:class:`raw_content`
        """
        # This attribute should be called text, because that's what requests does.
        try:
            return self.content.decode(self.charset, "strict")
        except (TypeError, UnicodeError):
            # UnicodeError: The encoding does not fit
            # TypeError: self.encoding is None
            return self.content.decode("utf-8", "surrogateescape")

    @text.setter
    def text(self, text):
        try:
            self.content = text.encode(self.charset, "strict")
        except (TypeError, UnicodeError):
            # UnicodeError: The encoding does not fit
            # TypeError: self.encoding is None
            self.content = text.encode("utf-8", "surrogateescape")

    def decode(self):
        """
            Decodes body based on the current Content-Encoding header, then
            removes the header. If there is no Content-Encoding header, no
            action is taken.

            Returns:
                The previous content encoding, if decoding succeeded.
                False, decoding failed.
        """
        # TODO: This should raise an exception rather than failing silently.
        ce = self.headers.get("content-encoding")
        if not ce:
            return False
        try:
            self.content = encoding.decode(ce, self.content)
        except encoding.CodecException:
            return False
        else:
            self.headers.pop("content-encoding", None)
            return ce

    def encode(self, e):
        """
            Encodes body with the encoding e, where e is "gzip", "deflate" or "identity".

            Returns:
                True, if decoding succeeded.
                False, otherwise.
        """
        try:
            self.content = encoding.encode(e, self.content)
        except encoding.CodecException:
            return False
        else:
            self.headers["content-encoding"] = e
            return True

    # Legacy

    @property
    def body(self):  # pragma: nocover
        warnings.warn(".body is deprecated, use .(raw_)content instead.", DeprecationWarning)
        return self.raw_content

    @body.setter
    def body(self, body):  # pragma: nocover
        warnings.warn(".body is deprecated, use .(raw_)content instead.", DeprecationWarning)
        self.raw_content = body


class _decoded(object):
    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        pass


def decoded(message):
    warnings.warn("decoded() is deprecated, use .content instead (which is now always decoded).", DeprecationWarning)
    return _decoded()
