from goapitest.getapidata.processdata import DiffDataProcessMixin


def test_diff_data_process_mixin_diff_normal():
    compared_to = {'key': 1}
    be_compared = {'key': 1}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) is None

    compared_to = {'key': {'key1': 1}}
    be_compared = {'key': {'key1': 1}}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) is None


def test_diff_data_process_mixin_diff_strict():
    compared_to = {'key': [1, 2, 3]}
    be_compared = {'key': [3, 2, 1]}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) == ['key']
    assert DiffDataProcessMixin.diff(compared_to, be_compared, strict=False) is None


def test_diff_data_process_mixin_diff_key_error():
    compared_to = {'key': 1}
    be_compared = {'ikey': 2}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) == ['ikey', '~']


def test_diff_data_process_mixin_diff_value_not_equal():
    compared_to = {'key': [1, 2, 3]}
    be_compared = {'key': {'key1': 1}}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) == ['key']

    compared_to = {'key': [1, 2, 3]}
    be_compared = {'key': 1}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) == ['key']

    compared_to = {'key': 2}
    be_compared = {'key': 1}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) == ['key']


def test_diff_data_process_mixin_diff_nest():
    compared_to = {'key': {'keyn1': 1, 'keyn2': 2}, 'key1': 1}
    be_compared = {'key': {'keyn1': 1, 'keyn2': 2}, 'key1': 2}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) == ['key1']

    compared_to = {'key': {'keyn1': 1}}
    be_compared = {'key': {'keyn1': 2}}
    assert DiffDataProcessMixin.diff(compared_to, be_compared) == ['key', 'keyn1']