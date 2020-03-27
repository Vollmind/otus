from log_analyzer import log_parse, report_compute


# log_parse
def test_log_parse_normal():
    data = [
        'elem0 elem1 elem2 elem3 elem4 elem5 elem6 url elemN 0.001'
    ]
    result = log_parse(data, 0.1)
    assert result == [('url', 0.001)], result


def test_log_parse_error():
    data = [
        'elem3 elem4 elem5 elem6 url elemN 0.001'
    ]
    result = None
    try:
        result = log_parse(data, 0.1)
    except RuntimeError as e:
        assert str(e) == 'Too many parsing exceptions - 1.0'
    assert result is None


def test_log_parse_error_percent():
    data_bad = [
        'elem3 elem4 elem5 elem6 url elemN 0.001',
        'elem3 elem4 elem5 elem6 url elemN 0.001',
        'elem3 elem4 elem5 elem6 url elemN 0.001',
        'elem0 elem1 elem2 elem3 elem4 elem5 elem6 url elemN 0.001',
        'elem0 elem1 elem2 elem3 elem4 elem5 elem6 url elemN 0.002'
    ]
    data_good = [
        'elem3 elem4 elem5 elem6 url elemN 0.001',
        'elem0 elem1 elem2 elem3 elem4 elem5 elem6 url elemN 0.001',
        'elem0 elem1 elem2 elem3 elem4 elem5 elem6 url elemN 0.002'
    ]
    result = None
    try:
        result = log_parse(data_bad, 0.5)
    except RuntimeError as e:
        assert str(e) == 'Too many parsing exceptions - 0.6'

    result = log_parse(data_good, 0.5)
    assert result == [('url', 0.001), ('url', 0.002)]


# report_compute
def test_report_compute_one_value():
    log_data = [
        ('url', 0.001)
    ]
    result = report_compute(log_data, 10)
    expected_result = [
        {
            'url': 'url',
            'count': 1,
            'count_perc': '1.000',
            'time_sum': '0.001',
            'time_perc': '1.000',
            'time_avg': '0.001',
            'time_max': '0.001',
            'time_med': '0.001'
        }
    ]
    assert result == expected_result, result


def test_report_compute_some_values():
    log_data = [
        ('url', 0.001),
        ('url', 0.003),
        ('url2', 0.001)
    ]
    result = report_compute(log_data, 10)
    expected_result = [
        {
            'url': 'url',
            'count': 2,
            'count_perc': '0.667',
            'time_sum': '0.004',
            'time_perc': '0.800',
            'time_avg': '0.002',
            'time_max': '0.003',
            'time_med': '0.002'
        },
        {
            'url': 'url2',
            'count': 1,
            'count_perc': '0.333',
            'time_sum': '0.001',
            'time_perc': '0.200',
            'time_avg': '0.001',
            'time_max': '0.001',
            'time_med': '0.001'
        }
    ]
    assert result == expected_result, result


def test_report_compute_corrupted():
    log_data = [
        ('url_pre_error', 0.001),
        ('url', 0.003),
        ('url', 'error!'),
        ('url', 0.003),
        ('url2', 0.001)
    ]
    result = []
    try:
        result = report_compute(log_data, 10)
    except TypeError as e:
        assert str(e) == "unsupported operand type(s) for +: 'float' and 'str'"
    assert result == [], result


def test_report_compute_count():
    log_data = [
        ('url', 0.001),
        ('url', 0.003),
        ('url2', 0.001)
    ]
    result = report_compute(log_data, 1)
    expected_result = [
        {
            'url': 'url',
            'count': 2,
            'count_perc': '0.667',
            'time_sum': '0.004',
            'time_perc': '0.800',
            'time_avg': '0.002',
            'time_max': '0.003',
            'time_med': '0.002'
        }
    ]
    assert result == expected_result, result
