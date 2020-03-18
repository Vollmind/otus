from unittest import mock

from log_analyzer import get_last_log


# get_last_log

@mock.patch('log_analyzer.os.listdir', return_value=['nginx-access-ui.log-20170630',
                                                     'nginx-access-ui.log-20170830'])
def test_get_last_log_correct(_):
    file = get_last_log('.')
    assert file.file_path == './nginx-access-ui.log-20170830', file.file_path
    assert file.date.strftime('%d.%m.%Y') == '30.08.2017', file.date


@mock.patch('log_analyzer.os.listdir', return_value=['nginx-access-ui.log-20170630.gz',
                                                     'nginx-access-ui.log-20170830.gz'])
def test_get_last_log_correct_gzip(_):
    file = get_last_log('.')
    assert file.file_path == './nginx-access-ui.log-20170830.gz', file.file_path
    assert file.date.strftime('%d.%m.%Y') == '30.08.2017', file.date


@mock.patch('log_analyzer.os.listdir', return_value=[])
def test_get_last_log_nolog(_):
    file = get_last_log('.')
    assert file is None


@mock.patch('log_analyzer.os.listdir', return_value=['nginx-access-ui.log-20170630.gz2',
                                                     'nginx-access-ui.log-20170630.aaa',
                                                     'nginx-other_serv.log-20170630.gz',
                                                     'AAAnginx-access-ui.log-20170630.gz',
                                                     '1'])
def test_get_last_log_other_logs(_):
    file = get_last_log('.')
    assert file is None
