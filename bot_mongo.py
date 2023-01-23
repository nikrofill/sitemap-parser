import logging
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

class LinkCheckerDB:
    def __init__(self):
        self.db_url = os.environ['DB_URI']
        self.db_name = os.environ['DB_NAME']
        self.client = MongoClient(self.db_url)
        self.db = self.client[self.db_name]
        logging.info("Database initialized")
    
    def log_check(self, result):
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)

        for check in result:
            url = check['url']
            status_code = int(check.get('status', 'Error'))

            url_doc = self.db.links.find_one({'url': url})
            if not url_doc:
                url_doc = {'_id': self.db.links.insert_one({'url': url}).inserted_id}

            check_entry = self.db.checks.find_one({
                'date': today,
                'status_code': status_code
            })

            if check_entry:
                if url_doc['_id'] not in check_entry['url_ids']:
                    self.db.checks.update_one(
                        {'_id': check_entry['_id']},
                        {
                            '$addToSet': {'url_ids': url_doc['_id']}
                        }
                    )
            else:
                self.db.checks.insert_one({
                    'date': today,
                    'status_code': status_code,
                    'total_checks': 1,
                    'url_ids': [url_doc['_id']]
                })

        if result:
            status_codes = set(check.get('status', 'Error') for check in result)
            for code in status_codes:
                try:
                    status = int(code)
                except ValueError:
                    status = 'Error'
                self.db.checks.update_one(
                    {'date': today, 'status_code': status},
                    {'$inc': {'total_checks': 1}},
                    upsert=True
                )

    def generate_slack_message(self):
        attachments = []
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day)

        checks = list(self.db.checks.find({'date': {'$gte': yesterday_start, '$lt': yesterday_start + timedelta(days=1)}}))
        total_checks = sum(check.get('total_checks', 0) for check in checks)

        report_block = {
            "color": "#f2c744",
            "blocks": [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Report by {yesterday.strftime('%Y-%m-%d')}\nTotal number of checks: {total_checks}"
                }
            }]
        }
        attachments.append(report_block)


        # successful_checks_text = "Successful checks:\n"
        # successful_checks = any(check['status_code'] == 200 for check in checks)
        # if successful_checks:
        #     successful_checks_text += "\n".join(f"<{self.db.links.find_one({'_id': url_id})['url']}>"
        #                                         for check in checks if check['status_code'] == 200
        #                                         for url_id in check['url_ids'])
        # else:
        #     successful_checks_text += "No Data"

        # successful_checks_block = {
        #     "color": "#36a64f",
        #     "blocks": [{
        #         "type": "section",
        #         "text": {"type": "mrkdwn", "text": successful_checks_text}
        #     }]
        # }
        # attachments.append(successful_checks_block)


        non_200_checks_text = "Response != 200:\n"
        non_200_checks = any(check['status_code'] != 200 for check in checks)
        if non_200_checks:
            non_200_checks_text += "\n".join(f"<{self.db.links.find_one({'_id': url_id})['url']}>"
                                             for check in checks if check['status_code'] != 200
                                             for url_id in check['url_ids'])
        else:
            non_200_checks_text += "No Data"

        non_200_checks_block = {
            "color": "#ff0000",
            "blocks": [{
                "type": "section",
                "text": {"type": "mrkdwn", "text": non_200_checks_text}
            }]
        }
        attachments.append(non_200_checks_block)

        return attachments