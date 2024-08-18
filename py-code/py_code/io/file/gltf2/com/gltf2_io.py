import sys
import traceback


def from_int(x):
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x):
    assert x is None
    return x


def from_union(fs, x):
    tracebacks = []
    for f in fs:
        try:
            return f(x)
        except AssertionError:
            _, _, tb = sys.exc_info()
            tracebacks.append(tb)
    for tb in tracebacks:
        traceback.print_tb(tb)  # Fixed format
        tb_info = traceback.extract_tb(tb)
        for tbi in tb_info:
            filename, line, func, text = tbi
            print(
                "ERROR",
                "An error occurred on line {} in statement {}".format(line, text),
            )
    assert False


def from_dict(f, x):
    assert isinstance(x, dict)
    return {k: f(v) for (k, v) in x.items()}


def to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()


def from_list(f, x):
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x):
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_str(x):
    assert isinstance(x, str)
    return x


def from_bool(x):
    assert isinstance(x, bool)
    return x


def to_float(x):
    assert isinstance(x, float)
    return x


def extension_to_dict(obj):
    if hasattr(obj, "to_list"):
        obj = obj.to_list()
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    if isinstance(obj, list):
        return [extension_to_dict(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: extension_to_dict(v) for (k, v) in obj.items()}
    return obj


def from_extension(x):
    x = extension_to_dict(x)
    assert isinstance(x, dict)
    return x


def from_extra(x):
    return extension_to_dict(x)


class AccessorSparseIndices:
    """Index array of size `count` that points to those accessor attributes that deviate from
    their initialization value. Indices must strictly increase.

    Indices of those attributes that deviate from their initialization value.
    """

    def __init__(self, buffer_view, byte_offset, component_type, extensions, extras):
        self.buffer_view = buffer_view
        self.byte_offset = byte_offset
        self.component_type = component_type
        self.extensions = extensions
        self.extras = extras

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        buffer_view = from_int(obj.get("bufferView"))
        byte_offset = from_union([from_int, from_none], obj.get("byteOffset"))
        component_type = from_int(obj.get("componentType"))
        extensions = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("extensions"),
        )
        extras = obj.get("extras")
        return AccessorSparseIndices(
            buffer_view, byte_offset, component_type, extensions, extras
        )

    def to_dict(self):
        result = {}
        result["bufferView"] = from_int(self.buffer_view)
        result["byteOffset"] = from_union([from_int, from_none], self.byte_offset)
        result["componentType"] = from_int(self.component_type)
        result["extensions"] = from_union(
            [lambda x: from_dict(from_extension, x), from_none], self.extensions
        )
        result["extras"] = from_extra(self.extras)
        return result


class AccessorSparseValues:
    """Array of size `count` times number of components, storing the displaced accessor
    attributes pointed by `indices`. Substituted values must have the same `componentType`
    and number of components as the base accessor.

    Array of size `accessor.sparse.count` times number of components storing the displaced
    accessor attributes pointed by `accessor.sparse.indices`.
    """

    def __init__(self, buffer_view, byte_offset, extensions, extras):
        self.buffer_view = buffer_view
        self.byte_offset = byte_offset
        self.extensions = extensions
        self.extras = extras

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        buffer_view = from_int(obj.get("bufferView"))
        byte_offset = from_union([from_int, from_none], obj.get("byteOffset"))
        extensions = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("extensions"),
        )
        extras = obj.get("extras")
        return AccessorSparseValues(buffer_view, byte_offset, extensions, extras)

    def to_dict(self):
        result = {}
        result["bufferView"] = from_int(self.buffer_view)
        result["byteOffset"] = from_union([from_int, from_none], self.byte_offset)
        result["extensions"] = from_union(
            [lambda x: from_dict(from_extension, x), from_none], self.extensions
        )
        result["extras"] = from_extra(self.extras)
        return result


class AccessorSparse:
    """Sparse storage of attributes that deviate from their initialization value."""

    def __init__(self, count, extensions, extras, indices, values):
        self.count = count
        self.extensions = extensions
        self.extras = extras
        self.indices = indices
        self.values = values

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        count = from_int(obj.get("count"))
        extensions = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("extensions"),
        )
        extras = obj.get("extras")
        indices = AccessorSparseIndices.from_dict(obj.get("indices"))
        values = AccessorSparseValues.from_dict(obj.get("values"))
        return AccessorSparse(count, extensions, extras, indices, values)

    def to_dict(self):
        result = {}
        result["count"] = from_int(self.count)
        result["extensions"] = from_union(
            [lambda x: from_dict(from_extension, x), from_none], self.extensions
        )
        result["extras"] = from_extra(self.extras)
        result["indices"] = to_class(AccessorSparseIndices, self.indices)
        result["values"] = to_class(AccessorSparseValues, self.values)
        return result


class Accessor:
    """A typed view into a bufferView.  A bufferView contains raw binary data.  An accessor
    provides a typed view into a bufferView or a subset of a bufferView similar to how
    WebGL's `vertexAttribPointer()` defines an attribute in a buffer.
    """

    def __init__(
        self,
        buffer_view,
        byte_offset,
        component_type,
        count,
        extensions,
        extras,
        max,
        min,
        name,
        normalized,
        sparse,
        type,
    ):
        self.buffer_view: int = buffer_view
        self.byte_offset = byte_offset
        self.component_type = component_type
        self.count = count
        self.extensions = extensions
        self.extras = extras
        self.max = max
        self.min = min
        self.name = name
        self.normalized = normalized
        self.sparse = sparse
        self.type = type

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        buffer_view = from_union([from_int, from_none], obj.get("bufferView"))
        byte_offset = from_union([from_int, from_none], obj.get("byteOffset"))
        component_type = from_int(obj.get("componentType"))
        count = from_int(obj.get("count"))
        extensions = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("extensions"),
        )
        extras = obj.get("extras")
        max = from_union(
            [lambda x: from_list(from_float, x), from_none], obj.get("max")
        )
        min = from_union(
            [lambda x: from_list(from_float, x), from_none], obj.get("min")
        )
        name = from_union([from_str, from_none], obj.get("name"))
        normalized = from_union([from_bool, from_none], obj.get("normalized"))
        sparse = from_union([AccessorSparse.from_dict, from_none], obj.get("sparse"))
        type = from_str(obj.get("type"))
        return Accessor(
            buffer_view,
            byte_offset,
            component_type,
            count,
            extensions,
            extras,
            max,
            min,
            name,
            normalized,
            sparse,
            type,
        )

    def to_dict(self):
        result = {}
        result["bufferView"] = from_union([from_int, from_none], self.buffer_view)
        result["byteOffset"] = from_union([from_int, from_none], self.byte_offset)
        result["componentType"] = from_int(self.component_type)
        result["count"] = from_int(self.count)
        result["extensions"] = from_union(
            [lambda x: from_dict(from_extension, x), from_none], self.extensions
        )
        result["extras"] = from_extra(self.extras)
        result["max"] = from_union(
            [lambda x: from_list(to_float, x), from_none], self.max
        )
        result["min"] = from_union(
            [lambda x: from_list(to_float, x), from_none], self.min
        )
        result["name"] = from_union([from_str, from_none], self.name)
        result["normalized"] = from_union([from_bool, from_none], self.normalized)
        result["sparse"] = from_union(
            [lambda x: to_class(AccessorSparse, x), from_none], self.sparse
        )
        result["type"] = from_str(self.type)
        return result


class BufferView:
    """A view into a buffer generally representing a subset of the buffer."""

    def __init__(
        self,
        buffer,
        byte_length,
        byte_offset,
        byte_stride,
        extensions,
        extras,
        name,
        target,
    ):
        self.buffer = buffer
        self.byte_length = byte_length
        self.byte_offset = byte_offset
        self.byte_stride = byte_stride
        self.extensions = extensions
        self.extras = extras
        self.name = name
        self.target = target

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        buffer = from_int(obj.get("buffer"))
        byte_length = from_int(obj.get("byteLength"))
        byte_offset = from_union([from_int, from_none], obj.get("byteOffset"))
        byte_stride = from_union([from_int, from_none], obj.get("byteStride"))
        extensions = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("extensions"),
        )
        extras = obj.get("extras")
        name = from_union([from_str, from_none], obj.get("name"))
        target = from_union([from_int, from_none], obj.get("target"))
        return BufferView(
            buffer,
            byte_length,
            byte_offset,
            byte_stride,
            extensions,
            extras,
            name,
            target,
        )

    def to_dict(self):
        result = {}
        result["buffer"] = from_int(self.buffer)
        result["byteLength"] = from_int(self.byte_length)
        result["byteOffset"] = from_union([from_int, from_none], self.byte_offset)
        result["byteStride"] = from_union([from_int, from_none], self.byte_stride)
        result["extensions"] = from_union(
            [lambda x: from_dict(from_extension, x), from_none], self.extensions
        )
        result["extras"] = from_extra(self.extras)
        result["name"] = from_union([from_str, from_none], self.name)
        result["target"] = from_union([from_int, from_none], self.target)
        return result


class Buffer:
    """A buffer points to binary geometry, animation, or skins."""

    def __init__(self, byte_length, extensions, extras, name, uri):
        self.byte_length = byte_length
        self.extensions = extensions
        self.extras = extras
        self.name = name
        self.uri = uri

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        byte_length = from_int(obj.get("byteLength"))
        extensions = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("extensions"),
        )
        extras = obj.get("extras")
        name = from_union([from_str, from_none], obj.get("name"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        return Buffer(byte_length, extensions, extras, name, uri)

    def to_dict(self):
        result = {}
        result["byteLength"] = from_int(self.byte_length)
        result["extensions"] = from_union(
            [lambda x: from_dict(from_extension, x), from_none], self.extensions
        )
        result["extras"] = from_extra(self.extras)
        result["name"] = from_union([from_str, from_none], self.name)
        result["uri"] = from_union([from_str, from_none], self.uri)
        return result

class Image:
    """Image data used to create a texture. Image can be referenced by URI or `bufferView`
    index. `mimeType` is required in the latter case.
    """

    def __init__(self, buffer_view, extensions, extras, mime_type, name, uri):
        self.buffer_view = buffer_view
        self.extensions = extensions
        self.extras = extras
        self.mime_type = mime_type
        self.name = name
        self.uri = uri

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        buffer_view = from_union([from_int, from_none], obj.get("bufferView"))
        extensions = from_union([lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                                obj.get("extensions"))
        extras = obj.get("extras")
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        name = from_union([from_str, from_none], obj.get("name"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        return Image(buffer_view, extensions, extras, mime_type, name, uri)

    def to_dict(self):
        result = {}
        result["bufferView"] = from_union([from_int, from_none], self.buffer_view)
        result["extensions"] = from_union([lambda x: from_dict(from_extension, x), from_none],
                                          self.extensions)
        result["extras"] = from_extra(self.extras)
        result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        result["name"] = from_union([from_str, from_none], self.name)
        result["uri"] = from_union([from_str, from_none], self.uri)
        return result
