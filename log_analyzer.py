#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import argparse
import gzip
import logging
import os
import re
import sys
from datetime import datetime
from itertools import groupby
from statistics import median
from string import Template

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "MAX_ERRORS": 0.1,
    "LOG_FILE": None
}

argparser = argparse.ArgumentParser(description='Create report for last log file')
argparser.add_argument('--config', help='Specify config file', default='./config.cfg')
argparser.add_argument('-vvs', help='For test')


def file_iter(filename, opener):
    with opener(filename, 'rt', encoding='utf-8') as file:
        for line in file:
            yield line


# parse config if need
args = argparser.parse_args()
if args.config:
    for conf_line in file_iter(args.config, open):
        if not re.match('[a-zA-Z_]+=.+', conf_line):
            raise ValueError('Wrong config option')
        conf_option, conf_value = conf_line.split('=')
        if conf_option not in config.keys():
            raise ValueError('Wrong config option')
        if conf_option == 'REPORT_SIZE':
            config[conf_option] = int(conf_value)
        elif conf_option == 'MAX_ERRORS':
            config[conf_option] = float(conf_value)
        else:
            config[conf_option] = conf_value

logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S',
                    filename=config['LOG_FILE'],
                    level=logging.INFO)


# Catch unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def get_last_log(folder):
    """
    Search last log in folder - there is date in log name
    :param folder: folder with logs
    :return: tuple - file name, date of log, function to open it (depends on file format)
    """
    log_files = [x for x in os.listdir(folder) if re.fullmatch("nginx-access-ui\.log-[0-9]{8}(\.gz)?", x)]
    if len(log_files) == 0:
        return None, None, None
    last_log = max(log_files)
    splitted = last_log.split('.')
    return f'{folder}/{last_log}', \
           datetime.strptime(splitted[1][4:], '%Y%m%d'), \
           gzip.open if len(splitted) == 3 else open


def log_parse(line_iterator, max_errors):
    """
    Parse lines from log
    :param line_iterator: iterator with lines in format - '* * * * * * * url * * time'
    :param max_errors: raise error if percent of uncorrect formatted strings more than this
    :return: List of tuples - (url, time)
    """
    parsed_log = []
    current_errors = 0
    line_count = 0
    for line in line_iterator:
        line_count += 1
        url = None
        time = None
        try:
            splitted = line.split(' ')
            time = float(splitted[-1])
            url = splitted[7]
            parsed_log.append((url, time))
        except Exception:
            logging.exception(f'Error while parsing log: line {line_count}')
            current_errors += 1
    if current_errors/line_count > max_errors:
        raise ValueError(f'Too many parsing exceptions - {current_errors/line_count}')
    return parsed_log


def report_compute(log_data, report_size):
    """
    Prepare values to report
    :param log_data: List of tuples - (url, time)
    :param report_size: max urls in report
    :return: List of dicts for report
    """
    request_count = len(log_data)
    all_time = sum(x[1] for x in log_data)
    report_data = []
    for url, group_iter in groupby(sorted(log_data), key=lambda x: x[0]):
        time_data = [x[1] for x in group_iter]
        report_data.append({
            'url': url,
            'count': len(time_data),
            'count_perc': f'{len(time_data) / request_count:.3f}',
            'time_sum': f'{sum(time_data):.3f}',
            'time_perc': f'{sum(time_data) / all_time:.3f}',
            'time_avg': f'{sum(time_data) / len(time_data):.3f}',
            'time_max': f'{max(time_data):.3f}',
            'time_med': f'{median(time_data):.3f}'
        })
    return sorted(report_data, key=lambda x: x['time_sum'], reverse=True)[:report_size]


def report_create(template_name, result_name, report_data):
    """
    Creates report from template
    :param template_name: address of template file
    :param result_name: address of result file
    :param report_data: data for report
    """
    with open(result_name, 'w') as result_file:
        for line in file_iter(template_name, open):
            t = Template(line)
            result_file.write(t.safe_substitute(table_json=report_data))
    logging.info(f'Report created successfully - {result_name}')


def main():
    filename, filedate, opener = get_last_log(config['LOG_DIR'])
    if filename is None:
        # No log files in directory
        logging.info(f'No log found in {config["LOG_DIR"]}')
        return
    report_name = f'{config["REPORT_DIR"]}/report-{filedate.strftime("%Y.%m.%d")}.html'
    if os.path.exists(report_name):
        # report already exists!
        logging.info(f'Report {report_name} already exists!')
        return

    parsed_log = log_parse(file_iter(filename, opener), config['MAX_ERRORS'])
    report_data = report_compute(parsed_log, config['REPORT_SIZE'])
    report_create('./report.html', report_name, report_data)


if __name__ == "__main__":
    logging.info('Start')
    main()
    logging.info('End')
