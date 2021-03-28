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

    def __init__(self, file):
        self._file = file
        file.contents.clear()

    def write(self, text):
        self._file.contents.append(text)


class FileReader:

    def __init__(self, file):
        self._file = file

    def read(self):
        return ''.join(self._file.contents)


class MockFileSystem:

    def __init__(self):
        self._root = Directory()

    @contextmanager
    def open(self, path, mode='r'):
        if mode == 'r':
            file = self._open_for_text_reading(path)
        elif mode == 'w':
            file = self._open_for_text_writing(path)
        else:
            1/0
        yield file

    def _open_for_text_reading(self, path):
        maybe_file = self._root[path]
        if maybe_file is None:
            1/0
        elif isinstance(maybe_file, File):
            return FileReader(maybe_file)
        elif isinstance(maybe_file, Directory):
            1/0
        else:
            1/0

    def _open_for_text_writing(self, path):
        try:
            maybe_file = self._root[path]
        except KeyError:
            file = File()
            self._root[path] = file
            return FileWriter(file)
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
    assert text == 'ok'
