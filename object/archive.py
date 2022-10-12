from collections import namedtuple

import sql.blog  # 不用 from import 避免循环导入
from sql.archive import (read_archive,
                         create_archive,
                         get_archive_list,
                         get_blog_archive,
                         delete_archive,
                         add_blog_to_archive,
                         sub_blog_from_archive)
from sql.statistics import get_archive_click


class _Archive:
    archive_tuple = namedtuple('Archive', 'name describe')

    @staticmethod
    def get_archive_list():
        ret = []
        for i in get_archive_list():
            ret.append(Archive(i))
        return ret


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
        return Archive.archive_tuple(*read_archive(self.id))

    @property
    def name(self):
        return self.info.name

    @property
    def describe(self):
        return self.info.describe

    @property
    def count(self):
        return sql.blog.get_archive_blog_count(self.id)

    @property
    def clicks(self):
        return get_archive_click(self.id)

    def is_delete(self):
        return len(self.name) != 0

    def delete(self):
        return delete_archive(self.id)

    def add_blog(self, blog_id: int):
        add_blog_to_archive(blog_id, self.id)

    def sub_blog(self, blog_id: int):
        sub_blog_from_archive(blog_id, self.id)
