from typing import Optional

from sql.archive import get_archive_id_by_name, create_archive, get_archive_list, read_archive, delete_archive


def load_archive_by_name(name: str) -> "Optional[Archive]":
    archive_id, describe = get_archive_id_by_name(name)
    if archive_id is None:
        return None
    return Archive(name, describe, archive_id)


class Archive:
    def __init__(self, name, describe, archive_id):
        self.name = name
        self.describe = describe
        self.archive_id = archive_id

    @staticmethod
    def get_archive_list():
        return get_archive_list()

    @staticmethod
    def get_blog_archive(blog_id: int):
        archive = read_archive(blog_id)
        archive_list = []
        for i in archive:
            archive_list.append(Archive(i[1], i[2], i[0]))
        return archive_list

    def create(self):
        return create_archive(self.name, self.describe)

    def delete(self):
        return delete_archive(self.archive_id)