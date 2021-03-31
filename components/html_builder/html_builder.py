from htmlclasses import E, to_string
import pathlib
import textwrap

STATIC_FILES_FOLDER = 'data'
ABSOLUTE_CONTENT_PATH = str(pathlib.Path('/') / STATIC_FILES_FOLDER)


class RealFileSystem:

    def open(self, path, mode='r'):
        return open(pathlib.Path('/').joinpath(*path), mode)

    def mkdir(self, path, exist_ok=False):
        pathlib.Path('/').joinpath(*path).mkdir(exist_ok=exist_ok)


class html(E):

    class head(E):

        class title:
            TEXT = 'Aggregated public information about British schools'

        class meta:
            charset = 'UTF-8'

        class meta:
            name = 'description'
            content = (
                'Public school information, such as OFSTED ratings, displayed'
                + ' on a map. No JavaScript required.'
                )

        class meta:
            name = 'keywords'
            content = ''

        class meta:
            name = 'viewport'
            content = 'width=device-width, initial-scale=1.0'

        class link:
            
            rel = 'stylesheet'
            href = 'style.css'
            

    class body(E):

        class strong:

            class h1:

                TEXT = 'Under construction'

        class p:

            TEXT = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac fermentum magna, sed tempus justo. Etiam justo sapien, facilisis non viverra hendrerit, consectetur ut felis. Praesent sit amet ultricies erat, sed sagittis nisl. Etiam neque diam, consequat in lacus in, molestie pulvinar nunc. Ut sit amet tellus quis lectus fringilla malesuada. Duis fermentum dictum elit vel eleifend. Sed tincidunt quam at dolor mattis, vel condimentum lorem lacinia. Vivamus rhoncus metus quis sapien euismod, sed pulvinar diam interdum. Nam ligula turpis, posuere eu nibh et, cursus dapibus metus. Fusce ac bibendum turpis. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Sed tempor magna id urna tincidunt commodo. Vivamus ultricies quam eros, vel consequat sem vestibulum vitae. Sed vestibulum hendrerit tellus, et iaculis ipsum sodales sit amet. 
            '''


def create_file(fs):
    fs.mkdir((STATIC_FILES_FOLDER,), exist_ok=True)

    content = to_string(html(), indent='  ')
    print('Writing:\n')
    print(content)
    with fs.open((STATIC_FILES_FOLDER, 'index.html',), 'wb') as fh:
        fh.write(content.encode('utf-8'))


def create_css_file(fs):
    fs.mkdir((STATIC_FILES_FOLDER,), exist_ok=True)

    content = textwrap.dedent('''
        html {
            font-family: "Courier New", Courier, monospace;
            max-width: 64ch;
            margin: auto;
        }
        h1 {
            text-align: center;
        }
        ''')
    print('Writing:\n')
    print(content)
    with fs.open((STATIC_FILES_FOLDER, 'style.css',), 'wb') as fh:
        fh.write(content.encode('utf-8'))


if __name__ == '__main__':
    fs = RealFileSystem()
    create_file(fs)
    create_css_file(fs)
