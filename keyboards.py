from aiogram.types import (KeyboardButton,
                           ReplyKeyboardMarkup,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)


kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton(text='/help')
b2 = KeyboardButton(text='/description')
b3 = KeyboardButton(text='Icons!')

kb.add(b3).add(b1, b2)

kb_photo = ReplyKeyboardMarkup(resize_keyboard=True)
b1_photo = KeyboardButton(text='Get icons')
b2_photo = KeyboardButton(text='Main menu')
b3_photo = KeyboardButton(text='History')
kb_photo.add(b1_photo, b2_photo).add(b3_photo)

ikb = InlineKeyboardMarkup()
ib1 = InlineKeyboardButton(text='👍',
                           callback_data='like')
ib2 = InlineKeyboardButton(text='👎',
                           callback_data='dislike')
ib3 = InlineKeyboardButton(text="Main menu", callback_data='main')

kb_back = ReplyKeyboardMarkup(resize_keyboard=True)
kb_back.add(KeyboardButton(text='Main menu'))

ikb.add(ib1, ib2).add(ib3)

