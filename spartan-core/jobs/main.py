import logging.config
import os
import sys
import schedule as schedule

import time

import yaml

def job():
    logger.info("run job")


dir_path = os.path.dirname(os.path.realpath(__file__))
cfg_file = os.path.join(os.path.dirname(dir_path), 'conf', 'log_conf.yaml')

with open(cfg_file, 'rt') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
logger = logging.getLogger("spartan.scheduler")





logger.info("initialize scheduler")
#schedule.every(30).seconds.do(job)
schedule.every().day.at("07:32").do(job)

if __name__ == '__main__':
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error("got error", e)
        except KeyboardInterrupt:
            print("got keyboard interrupt")
            sys.exit(0)

