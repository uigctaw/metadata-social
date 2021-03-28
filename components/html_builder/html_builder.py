import pathlib

STATIC_FILES_FOLDER = 'data'
ABSOLUTE_CONTENT_PATH = str(pathlib.Path('/') / STATIC_FILES_FOLDER)


class RealFileSystem:

    def open(self, path, mode='r'):
        return open(pathlib.Path('/').joinpath(*path), mode)

    def mkdir(self, path, exist_ok=False):
        pathlib.Path('/').joinpath(*path).mkdir(exist_ok=exist_ok)


def create_file(fs):
    fs.mkdir((STATIC_FILES_FOLDER,), exist_ok=True)
    with fs.open((STATIC_FILES_FOLDER, 'index.html',), 'w') as fh:
        fh.write('ok')


if __name__ == '__main__':
    fs = RealFileSystem()
    create_file(fs)
