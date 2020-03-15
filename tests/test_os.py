from unittest import mock

from log_analyzer import get_last_log


# get_last_log

@mock.patch('log_analyzer.os.listdir', return_value=['nginx-access-ui.log-20170630',
                                                     'nginx-access-ui.log-20170830'])
def test_get_last_log_correct(_):
    filename, filedate, opener = get_last_log('.')
    assert filename == './nginx-access-ui.log-20170830', filename
    assert filedate.strftime('%d.%m.%Y') == '30.08.2017', filedate
    assert opener is None, opener


@mock.patch('log_analyzer.os.listdir', return_value=['nginx-access-ui.log-20170630.gz',
                                                     'nginx-access-ui.log-20170830.gz'])
def test_get_last_log_correct_gzip(_):
    filename, filedate, opener = get_last_log('.')
    assert filename == './nginx-access-ui.log-20170830.gz', filename
    assert filedate.strftime('%d.%m.%Y') == '30.08.2017', filedate
    assert opener == 'gz', opener


@mock.patch('log_analyzer.os.listdir', return_value=[])
def test_get_last_log_nolog(_):
    filename, filedate, opener = get_last_log('.')
    assert filename is None
    assert filedate is None
    assert opener is None


@mock.patch('log_analyzer.os.listdir', return_value=['nginx-access-ui.log-20170630.gz2',
                                                     'nginx-access-ui.log-20170630.aaa',
                                                     'nginx-other_serv.log-20170630.gz',
                                                     'AAAnginx-access-ui.log-20170630.gz',
                                                     '1'])
def test_get_last_log_other_logs(_):
    filename, filedate, opener = get_last_log('.')
    assert filename is None
    assert filedate is None
    assert opener is None
