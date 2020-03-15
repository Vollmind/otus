# Log parsing
OTUS Python 2020-02 lession-1

## Purpose
Creating report from NGINX logs.

## Log format
Expecting file names:<br/>
nginx-access-ui.log-**YYYYMMDD**<br/>
nginx-access-ui.log-**YYYYMMDD**.gz
 
## Usage
```bash
python log_analyzer.py [--config conf_file]
```
Script has build-in config. To change it - specify **conf_file**.

If **conf_file** is specified - load config from it.
Default config file - ./config.cfg

## Unit-tests
```bash
pytest ./ -vvs
```

###Author
Frantsev Matvey

15.03.2020