from bot_mongo import LinkCheckerDB
import send_message
from dotenv import load_dotenv
load_dotenv()

mongo_work = LinkCheckerDB()

def reporter(event, context):

    attachments = mongo_work.generate_slack_message()
    send_message.report(attachments)