from contextlib import contextmanager

from html_builder import create_file, STATIC_FILES_FOLDER


class Directory:

    def __init__(self):
        self._tree = {}

    def __getitem__(self, path):
        this, *rest = path
        this_obj = self._tree[this]
        if rest:
            return this_obj[rest]
        else:
            return this_obj

    def __setitem__(self, path, item):
        this, *rest = path
        if rest:
            self._tree[this][rest] = item
        else:
            if this in self._tree:
                raise FileExistsError(f'{path} already exists')
            else:
                self._tree[this] = item


class File:

    def __init__(self):
        self.contents = []


class FileWriter:

    def __init__(self, file, binary):
        self._file = file
        self._binary = binary
        file.contents.clear()

    def write(self, string):
        if self._binary:
            if isinstance(string, bytes):
                byte_string = string
            else:
                1/0
        else:
            byte_string = string.encode()

        self._file.contents.append(string)


class FileReader:

    def __init__(self, file, binary):
        self._file = file
        self._binary = binary

    def read(self):
        contents = b''.join(self._file.contents)
        if self._binary:
            return contents
        else:
            return contents.decode()


class MockFileSystem:

    def __init__(self):
        self._root = Directory()

    @contextmanager
    def open(self, path, mode='r'):
        reading = self._open_for_reading
        writing = self._open_for_writing

        mode_to_fn = {
                'r': lambda: reading(path, binary=False),
                'rb': lambda: reading(path, binary=True),
                'w': lambda: writing(path, binary=False),
                'wb': lambda: writing(path, binary=True),
        }

        yield mode_to_fn[mode]()

    def _open_for_reading(self, path, binary):
        maybe_file = self._root[path]
        if maybe_file is None:
            1/0
        elif isinstance(maybe_file, File):
            return FileReader(maybe_file, binary=binary)
        elif isinstance(maybe_file, Directory):
            1/0
        else:
            1/0

    def _open_for_writing(self, path, binary):
        try:
            maybe_file = self._root[path]
        except KeyError:
            file = File()
            self._root[path] = file
            return FileWriter(file, binary=binary)
        else:
            if isinstance(maybe_file, File):
                return FileWriter(maybe_file)
            else:
                1/0

    def mkdir(self, path, exist_ok=False):
        try:
            self._root[path] = Directory()
        except FileExistsError:
            if exist_ok and isinstance(self._root[path], Directory):
                return
            raise


MFS = MockFileSystem


def test_file_is_written():
    mfs = MFS()
    create_file(mfs)
    with mfs.open((STATIC_FILES_FOLDER, 'index.html',)) as fh:
        text = fh.read()
    assert 'open data' in text
