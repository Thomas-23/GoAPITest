
class ProcessReturnData(object):
    """process method must be implemented for the api request response data, the return data as a
    parameter to process method, and it must be a iter, use this iter return data to complete other
    process, eg. compare, store to the db, test or anything else
    """

    def process(self, data_iter):
        raise NotImplementedError


class DiffDataProcessMixin(object):
    """ compare default is considered to be dict data,for both
    compare and be compared data, be compared data may be small or small scaled
    path is used to stored the not equal dict's key path, eg. key1 > key2 ...
    """

    @classmethod
    def diff(cls, compare_data, be_compared_data, strict=True, path=None):
        """ strict is used to compare list value, if strict is true, not sorted list to compare,
        it also compare with the list items order.
        :param compare_data:
        :param be_compared_data:
        :param strict:
        :return: return the error dict path if compare is diff or success return None
        """
        if not path:
            path = []
        try:
            for key, value in be_compared_data.items():
                path.append(key)
                temp = compare_data[key]
                if isinstance(value, list) and isinstance(temp, list):
                    if strict:
                        status = value == temp
                    else:
                        status = sorted(value) == sorted(temp)
                    if not status:
                        return path
                elif isinstance(value, dict) and isinstance(temp, dict):
                    ret = cls.diff(temp, value, strict=strict, path=path)
                    if ret:
                        return ret
                elif value == temp:
                    pass
                else:
                    return path
                path = []
        except KeyError:
            path.append('~')
            return path


class CaseProcessMixin(object):

    case_container = None

    @classmethod
    def check_case(cls, case_data):
        pass

    @classmethod
    def get_case(cls, case_id):
        if cls.case_container is None:
            raise ValueError('case_container muse be defined you so you can get case to compared')
        return cls.case_container.get(case_id)

    @classmethod
    def write_case_result(cls, case_data, diff_return):
        pass

    @classmethod
    def get_failed_cases(cls):
        pass


class OutReportMixin(object):

    def report(self):
        pass

    def get_failed(self):
        pass


class SendAlertMixin(object):

    def send(self):
        pass

    def get_alerts(self):
        pass


class CaseReturnDataProcess(ProcessReturnData, DiffDataProcessMixin, CaseProcessMixin):

    def parse_response(self, data):
        return data

    def process(self, data_iter):
        for data in data_iter:
            print('process ------------')
            if data.response:
                diff_return = self.diff(self.parse_response(data.response), self.get_case(data.case_id))
                if diff_return:
                    self.write_case_result(data, diff_return)
                print(data.case_id, data.key, data.data)
            else:
                print('failed case {} request not success'.format(data.case_id))

    def get_failed(self):
        return self.get_failed_cases()


class FileApiReturnDataProcess(ProcessReturnData, DiffDataProcessMixin):

    def process(self, data_iter):
        for data in data_iter:
            if data.response is None:
                print('not diff the failed request')
            else:
                print(data.key, data.data)

case_data_process = CaseReturnDataProcess()

if __name__ == '__main__':

    def default_file_parser(f):
        data = []
        for line in f:
            temp = {}
            temp['method'] = 'get'
            clear_line = line.strip().split(',')
            if clear_line:
                temp['url'] = clear_line[1].strip()
                data.append(temp)
        return data

    def case_file_parser(f):
        data = []
        for line in f:
            temp = {}
            temp['method'] = 'get'
            clear_line = line.strip().split(',')
            if clear_line:
                temp['case_id'] = clear_line[0].strip()
                temp['url'] = clear_line[1].strip()
                data.append(temp)
        return data
    from goapitest.getapidata.apidata import GetDataFromFile
    from goapitest.getapidata.fetchdata import CaseFetchBase, FetchBase

    case_data = GetDataFromFile(r'C:\Users\long\Desktop\case_test.txt', case_file_parser)

    CaseFetchBase(case_data).fetch_data(thread=True)

    file_data = GetDataFromFile(r'C:\Users\long\Desktop\case_test.txt', default_file_parser)

    FetchBase(file_data, [FileApiReturnDataProcess()]).fetch_data(thread=True)