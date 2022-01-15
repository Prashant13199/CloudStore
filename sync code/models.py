"""
This module aims to create a model having the filesystem as backend, since
if someone don't want to add extra metadata more than the metadata given
by the file informations is useless to use a database.

TODO
    - traverse directory
    - check symlink
"""
from flask import current_app
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import datetime


class FilesystemObjectDoesNotExist(Exception):
    pass


class FilesystemObject(object):

    def __init__(self, filename, post=None, root=None):
        """Create an object from the information of the given filename or from a
        uploaded file.

        Example of usage:

            if request.method == 'POST' and 'photo' in request.POST:
                f = FilesystemObject('cats.png', request.POST['photo'])

        """
        self.root_dir = Path(root)
        self.p = os.path.join(self.root_dir,filename)
        name,ext = os.path.splitext(filename)
        size = 0
        if ext:
            self.size = round((os.path.getsize(os.path.join(self.root_dir,filename))/1024/1024),2)
        else:
            for path, dirs, files in os.walk(self.p):
                for f in files:
                    fp = os.path.join(path, f)
                    size += os.path.getsize(fp)
            self.size = round(size/1024/1024,2)
        self.date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(self.root_dir,filename))).strftime("%x")
        self.path = Path(filename if not post else secure_filename(post.filename))
        self.abspath = self.root_dir / self.path

        if post:
            self.upload(post)

        try:
            stats = os.stat(self.abspath)
            self.timestamp = stats.st_mtime
        except IOError as e:
            current_app.logger.error(e)
            current_app.logger.error(f'{self!r}')
            raise FilesystemObjectDoesNotExist(e)

    def __repr__(self):
        return f'<{self.__class__.__name__}(filename={self.path}, root={self.root_dir}, size={self.size}, date={self.date})>'

    def upload(self, post):
        """Get a POST file and save it to the settings.GALLERY_ROOT_DIR"""
        # TODO: handle filename conflicts
        # http://flask.pocoo.org/docs/patterns/fileuploads/
        current_app.logger.info(f'saving at \'{self.abspath}\'')
        post.save(str(self.abspath))

    @classmethod
    def all(cls, root):
        """Return a list of files contained in the directory pointed by settings.GALLERY_ROOT_DIR.
        """
        return [cls(filename=x, root=root) for x in os.listdir(root)]


class Image1(FilesystemObject):
    pass
