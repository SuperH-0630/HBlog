from sql.archive import (read_archive,
                         create_archive,
                         get_archive_list,
                         get_blog_archive,
                         delete_archive,
                         add_blog_to_archive,
                         sub_blog_from_archive)


class _Archive:
    @staticmethod
    def get_archive_list():
        return get_archive_list()

    @staticmethod
    def get_blog_archive(blog_id: int):
        archive_list = []
        for i in get_blog_archive(blog_id):
            archive_list.append(Archive(i))
        return archive_list

    @staticmethod
    def create(name, describe):
        ret = create_archive(name, describe)
        if ret is None:
            return None
        return Archive(ret)


class Archive(_Archive):
    def __init__(self, archive_id):
        self.id = archive_id

    @property
    def info(self):
        return read_archive(self.id)

    @property
    def name(self):
        return self.info[0]

    @property
    def describe(self):
        return self.info[1]

    def is_delete(self):
        return len(self.name) != 0

    def delete(self):
        return delete_archive(self.id)

    def add_blog(self, blog_id: int):
        add_blog_to_archive(blog_id, self.id)

    def sub_blog(self, blog_id: int):
        sub_blog_from_archive(blog_id, self.id)
