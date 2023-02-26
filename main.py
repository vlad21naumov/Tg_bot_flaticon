from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.future import select
# from config import TOKEN_API
from commands import HELP_COMMAND, DESCR_COMMAND, RAND, WELCOME, THEME, HISTORY
from keyboards import kb, kb_photo, ikb
from orm import Base, Users, Icons, engine
from parsing import get_icons
import random
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from states import UsersIcons
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN_API = os.getenv("TOKEN_API")
bot = Bot(TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

is_voted = False


async def on_startup(_):
    print('Bot has been started up')
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)


async def on_shutdown(_):
    print("Bot has been stopped")
    await engine.dispose()
    await dp.storage.close()
    await dp.storage.wait_closed()


async def list_of_icons(user_id):
    async with async_session() as session:
        stmt = select(Icons).where(Icons.user_id == user_id)
        result = await session.execute(stmt)
    return [u for u in result.scalars()]


@dp.message_handler(commands=['help'], state="*")
async def help_command(message: types.Message, state: FSMContext):
    await message.reply(text=HELP_COMMAND, parse_mode='HTML')


@dp.message_handler(commands=['description'], state="*")
async def descr_command(message: types.Message, state: FSMContext):
    await message.reply(text=DESCR_COMMAND, parse_mode='HTML')
    await message.delete()


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: types.Message, state: FSMContext):
    current_user = message.from_user
    await state.update_data(current_user=current_user)
    async with async_session() as session:
        stmt = select(Users).where(Users.user_id == current_user.id)
        result = await session.execute(stmt)
    res = result.scalars().first()
    if res is not None:
        print(f"Known user {current_user.full_name}")
        lr = await list_of_icons(current_user.id)
        if len(lr) == 0:
            await message.answer(
                    text=f"<em><b>Welcome, {current_user.full_name}!</b> You didn't use me. But I'm here and ready to help! 😉</em>",
                    parse_mode="HTML",
                    reply_markup=kb
                )
        else:
            last = lr[-1] 
            last_cat = last.category
            last_url = last.icon_url
            await message.answer(
                text=f"<em><b>Welcome, {current_user.full_name}!</b></em>\n" + f"Your last response: <b>{last_cat}</b> - {last_url}\n" +
                 "<em>But you may want something new! 😁</em>",
                parse_mode="HTML",
                reply_markup=kb
            )
            await message.delete()
    else:
        print(f"New user {current_user.full_name}")
        async with async_session() as session:
            async with session.begin():
                session.add_all([Users(
                                    user_id=current_user.id,
                                    user_login=current_user.username,
                                    user_name=current_user.full_name,
                                      )
                                ]
                               )
        print(f"Old user {current_user.full_name} -> to DB")


@dp.message_handler(Text(equals='Main menu'), state="*")
async def open_kb(message: types.Message, state: FSMContext):
    await message.answer(text=WELCOME,  
                         parse_mode='HTML',
                         reply_markup=kb)
    await message.delete()
    # await UsersIcons.default.set()


@dp.message_handler(Text(equals='Get icons'), state="*")
async def get_theme(message: types.Message, state: FSMContext):
    await message.answer(text=THEME)
    await message.delete()

    

@dp.message_handler(Text(equals='History'), state="*")
async def history(message: types.Message):
    await message.answer(text=HISTORY, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Main menu')))
    await UsersIcons.look_history.set()


@dp.message_handler(state=UsersIcons.look_history)
async def look_history(message: types.Message, state: FSMContext):
    print("LOOK HISTORY")
    async with state.proxy() as data:
        data['last_message'] = message.text
        user_data = await state.get_data()
        current_user = user_data['current_user']
        category = data['last_message']
        async with async_session() as session:
            stmt = select(Icons).where(Icons.user_id == current_user.id).where(Icons.category == category)
            result = await session.execute(stmt)
    hist = [ic for ic in result.scalars()]
    if len(hist) == 0:
        await message.answer(text='No history for such category 😢')
    else:
        await message.answer(text="\n".join([str(s.icon_url) for s in hist]))
    # await UsersIcons.default.set()



@dp.message_handler(Text(equals='Icons!'), state="*")
async def open_kb_photo(message: types.Message):
    await message.answer(text=RAND, 
                         parse_mode='HTML', 
                         reply_markup=kb_photo)
    await message.delete()
    # await UsersIcons.look_icon.set()


@dp.message_handler(state='*')
async def send_random_icons(message: types.Message, state: FSMContext):
    print('SEND ICONS')
    async with state.proxy() as data:
        data['last_message'] = message.text
        user_data = await state.get_data()
        current_user = user_data['current_user']
        category = data['last_message']
        icons = random.sample(get_icons(category), 1)
        data['icon_url'] = icons[0]
        await bot.send_photo(chat_id=message.chat.id,
                            photo=icons[0],
                            reply_markup=ikb)
        # await UsersIcons.default.set()



@dp.callback_query_handler(lambda c: c.data == 'like', state="*")
async def like_and_add(callback_query: types.CallbackQuery, state: FSMContext):
    print("LIKE AND ADD ICONS")
    global is_voted
    async with state.proxy() as data:
        user_data = await state.get_data()
        current_user = user_data['current_user']
        category = data['last_message']
        icon_url = data['icon_url']
        async with async_session() as session:
            async with session.begin():
                session.add_all(
                    [
                        Icons(
                            user_id=current_user.id,
                            icon_url=icon_url,
                            category=category,
                        )
                    ]
                )
    await callback_query.answer(text='Nice, I remembered 😏')
    is_voted = not is_voted


@dp.callback_query_handler(lambda c: c.data == 'dislike', state="*")
async def dislike_notadd(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer(text='Try next photo by entering new category ☺️')


@dp.callback_query_handler(lambda c: c.data == 'main', state="*")
async def back_to_main(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(text=WELCOME,
                                        parse_mode='HTML',
                                        reply_markup=kb)


if __name__ == "__main__":
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown)

    

