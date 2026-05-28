import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID", "")
CARD_NUMBER = os.getenv("CARD_NUMBER", "5614 6822 1620 9116")
CARD_OWNER = os.getenv("CARD_OWNER", "Xolmatov Jasur")
UZUM_CHANNEL_ID = os.getenv("UZUM_CHANNEL_ID", "")
SUNIY_INTELEKT_CHANNEL_ID = os.getenv("SUNIY_INTELEKT_CHANNEL_ID", "")
