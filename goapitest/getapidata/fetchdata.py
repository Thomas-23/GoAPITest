import logging
import requests
import hashlib
import inspect

from collections import OrderedDict, namedtuple
from concurrent import futures

from .storedata import url_request_problem_store
from .processdata import case_data_process

logger = logging.getLogger('goapitest.apidatabases')

Thread_Max = 20

Response_Data = namedtuple('response_data', 'key, data, response')
Case_Response_Data = namedtuple('case_response_data', ('case_id',) + Response_Data._fields)


class FetchBase(object):
    """ fetch class is used to get data from api request return, if the api is not a direct one,
    we need use our own request class, eg, the link in a page and then parse the page
    and get the other link, and one by one, and the last find our need finish request data.

    use a dict format data to do the request, it suitable for all request method

    action_objects is the data manipulation objects, you can use this api request data to store
    compare what ever
    """
    allow_method = ['get', 'post', 'put', 'option', 'delete', 'header']
    correct_status = [200, 302]

    def __init__(self, api_data: iter, action_objects: list, **kwargs):
        self.api_data = api_data
        self.action_objects = action_objects
        self.do_request = kwargs.get('my_request', None)
        if self.do_request:
            assert inspect.isfunction(self.do_request)

    @classmethod
    def unpackage_data(cls, data):
        """when data come from parser, you can unpackage it with the other format
        eg, the query params can be parse from a url
        :param data:
        :return:
        """
        return data

    def request_api(self, data):
        """request data from api you can you customize request to fetch data, if all the request is get
        i recommand you choise the tuple to simple request api, if others use the post , or you call all
        did with the dict
        :param data:
        :return:
        """
        ret_data = None
        copy_data = data.copy()
        try:
            if self.do_request:
                ret_data = self.do_request(data)
            elif isinstance(data, dict):
                method = data.pop('method', None)
                if not method:
                    raise ValueError('not find method in the data')
                if method not in self.allow_method:
                    raise ValueError('method {} is not allowed method, '
                                     'the only allow methods are: {}'.format(method, self.allow_method))
                session = requests.session()
                self.before_request(session, data)
                ret_data = getattr(session, method)(**data)
                print(ret_data)

            if ret_data is None:
                raise ValueError('{} is not a invalid api request data'.format(data))

            return self.filter(copy_data, ret_data)

        except:
            # any exception we call this connection error
            raise ConnectionError('requests api {} get connection error'.format(data))



    def before_request(self, session, data):
        """before request can auth, get token, cookie, all you can do in this function
        :param data:
        :return:
        """
        pass

    @classmethod
    def filter(cls, data, response):
        """clear response data, this will suitable for the manipulation object
        """

        url = data.get('url', None)
        if not url:
            raise ValueError('url key not in the data: {}'.format(data))

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = OrderedDict(sorted(data[key].items(), key=lambda t: t[0]))

        ordered_data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))

        id_key = hashlib.md5((ordered_data.__str__()).encode('utf-8')).hexdigest()

        logger.info(id_key)

        if response.status_code not in cls.correct_status:
            url_request_problem_store.create_or_update(code=response.status_code, data=data, key=id_key, content=response.text)
            return Response_Data(id_key, data, None)

        return Response_Data(id_key, data, response.text)

    def _do(self):
        for api in self.api_data:
            data = self.unpackage_data(api)
            yield self.request_api(data)

    def _thread_do(self):
        def run(api):
            data = self.unpackage_data(api)
            return self.request_api(data)

        with futures.ThreadPoolExecutor(Thread_Max) as executor:
            return executor.map(run, self.api_data)

    def fetch_data(self, thread: bool = True):
        """fetch data from api and the manipulation object use this data to process
        :return:
        """
        results = self._thread_do() if thread else self._do()
        for action_object in self.action_objects:
            action_object.process(results)


class CaseFetchBase(FetchBase):
    """when test api, if you have a cases list, you can use this one to get api data, and you must
    in the data include case_id_name, if not have this default is case_id, case_id represent a unique
    case, it only to know by case list, when differ the request return result with case expect result
    used is url generate md5 key not use the case_id
    """

    def __init__(self, case_data, action_objects: list= None, **kwargs):
        """default case process object is case_data_process
        :param case_data:
        :param action_objects:
        :param kwargs:
        :return:
        """
        action_objects = action_objects if action_objects else [case_data_process]
        case_id_name = kwargs.get('case_id_name', None)
        self.case_id_name = case_id_name if case_id_name else 'case_id'
        super(CaseFetchBase, self).__init__(case_data, action_objects, **kwargs)

    def unpackage_data(self, data):
        """clear the case_id from data
        :param data:
        :return:
        """
        print(data)
        case_id = data.pop(self.case_id_name, None)
        if not case_id:
            raise ValueError('case id is not in the case data, or the case id name is not set invalid you case '
                             'use case_id_name to specified you case id name with __init__ method')
        return case_id, data

    def _do(self):
        for api in self.api_data:
            case_id, data = self.unpackage_data(api)
            yield Case_Response_Data(case_id, *self.request_api(data))

    def _thread_do(self):
        def run(api):
            case_id, data = self.unpackage_data(api)
            return Case_Response_Data(case_id, *self.request_api(data))

        with futures.ThreadPoolExecutor(Thread_Max) as executor:
            return executor.map(run, self.api_data)
