from abc import abstractmethod
import inspect


class DataBaseMeta(type):
    """check generate_data function is a generator
    """

    @classmethod
    def _check_generate_data(meta, name, bases, attrs):
        # don't validate abstract class
        if bases != (object,):
            func = attrs.get('generate_data', None)
            if not func:
                raise ValueError('the {} is subclass GetDataBase, you should implement '
                                 'generate_data function but you did not.'.format(name))
            if not inspect.isgeneratorfunction(func):
                raise ValueError('generate_data function in subclass GetDataBase should be a generator')

    def __new__(cls, name, bases, attrs):
        cls._check_generate_data(name, bases, attrs)
        return super(DataBaseMeta, cls).__new__(cls, name, bases, attrs)


class GetDataBase(object, metaclass=DataBaseMeta):

    @abstractmethod
    def generate_data(self):
        pass

    def config(self, **kwargs):
        """before data generate, you can config parser or after generate you can config data
        :param kwargs:
        :return:
        """
        pass

    def __iter__(self):
        yield from self.generate_data()


def default_file_parser(f):
    data = []
    for line in f:
        clear_line = line.strip()
        if clear_line:
            data.append(clear_line)
    return data


class GetDataFromFile(GetDataBase):

    encoding = 'utf-8'

    def __init__(self, file_name, parser):
        self.parser = parser
        self.file_name = file_name
        # the data after parse
        self.parser_data = None

    def get_parser_data(self):
        with open(self.file_name, encoding=self.encoding) as f:
            self.parser_data = self.parser(f)

    def generate_data(self):
        self.get_parser_data()
        for data in self.parser_data:
            yield data


# if __name__ == "__main__":
#     GetDataFromFile()