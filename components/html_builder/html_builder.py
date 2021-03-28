import pathlib

STATIC_FILES_DIR = ('data',)


class RealFileSystem:

    open = open

    def mkdir(self, path, exist_ok=False):
        pathlib.Path('/').joinpath(*path).mkdir(exist_ok=exist_ok)


def create_file(fs):
    fs.mkdir(STATIC_FILES_DIR, exist_ok=True)
    with fs.open(STATIC_FILES_DIR + ('index.html',), 'w') as fh:
        fh.write('ok')


if __name__ == '__main__':
    fs = RealFileSystem()
    create_file(fs)
