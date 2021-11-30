from typing import Optional

from sql.file import get_file_id_by_name, create_file, get_file_list, read_file, delete_file


def load_file_by_name(name: str) -> "Optional[File]":
    file_id, describe = get_file_id_by_name(name)
    if file_id is None:
        return None
    return File(name, describe, file_id)


class File:
    def __init__(self, name, describe, file_id):
        self.name = name
        self.describe = describe
        self.id = file_id

    @staticmethod
    def get_file_list():
        return get_file_list()

    @staticmethod
    def get_blog_file(blog_id: int):
        file = read_file(blog_id)
        file_list = []
        for i in file:
            file_list.append(File(i[1], i[2], i[0]))
        return file_list

    def create(self):
        return create_file(self.name, self.describe)

    def delete(self):
        return delete_file(self.id)
