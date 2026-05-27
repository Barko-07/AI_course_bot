import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID", "")
CARD_NUMBER = os.getenv("CARD_NUMBER", "9860 1001 2668 1517")
CARD_OWNER = os.getenv("CARD_OWNER", "Sanjar Kamilov")
