from cryptography.fernet import Fernet
from flask import current_app as app


def encrypt_hash(data):
    try:
        f = Fernet(app.config.get('HASH_SECRET_KEY'))
        token = f.encrypt(str.encode(data))
        return token.decode()
    except:
        return None

def decrypt_hash(data):
    try:
        f = Fernet(app.config.get('HASH_SECRET_KEY'))
        return f.decrypt(str.encode(data)).decode()
    except Exception:
        return None


def return_card_number(userCard):
    card_2 = decrypt_hash(userCard.card_2)
    card_3 = decrypt_hash(userCard.card_3)
    card_4 = decrypt_hash(userCard.card_4)
    card_number = userCard.card_1 + "-" + card_2+"-" + card_3+"-" + card_4
    return card_number 
