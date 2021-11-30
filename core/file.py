from sql.file import get_file_id, create_file, get_file_list, get_blog_file


class LoadFileError(Exception):
    ...


def load_file_by_name(name: str) -> "File":
    file_id, describe = get_file_id(name)
    if file_id is None:
        raise LoadFileError
    return File(name, describe, file_id)


class File:
    def __init__(self, name, describe, file_id):
        self.name = name
        self.describe = describe
        self.id = file_id

    @staticmethod
    def get_file_list():
        return get_file_list()

    def create_file(self):
        return create_file(self.name, self.describe)

    @staticmethod
    def get_blog_file(blog_id: int):
        file = get_blog_file(blog_id)
        file_list = []
        for i in file:
            file_list.append(File(i[1], i[2], i[0]))
        return file_list
