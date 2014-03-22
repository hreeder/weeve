from eveapp import app, celery, db
import evelink

@celery.task()
def get_api_key_info(keyid):
	return None

@celery.task()
def get_character_sheet(charid):
	return None