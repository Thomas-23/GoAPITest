__all__ = ['url_request_problem_store']


class BaseStore(object):

    def create_or_update(self, **kwargs):
        raise NotImplementedError('process(**kwargs) must be overridden.')


class URLProblemStore(BaseStore):
    def create_or_update(self, **kwargs):
        print('url problem-------------')
        print(kwargs['code'], kwargs['data'], kwargs['key'])

url_request_problem_store = URLProblemStore()