import asyncio, os, sqlite3
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputMediaPhoto

TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = 7894051808
CHANNEL = '@hoqanft'
VPN_URL = 'https://t.me/CristyVPN_bot?start=7894051808'
APPLY_URL = 'https://t.me/+IxVXx6qkPEpjZTYy'
COMMENT_TEXT = '@hoqabot спс за букет 💐'
NFT_LINK = 'https://t.me/nft/SnoopCigar-36783'
DB = str(BASE_DIR / 'hoqabot.db')
IMG = str(BASE_DIR / 'images')

if not TOKEN:
    raise RuntimeError('BOT_TOKEN is not set')
bot = Bot(TOKEN)
dp = Dispatcher()


def db():
    con = sqlite3.connect(DB)
    con.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_seen TEXT, last_seen TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS actions (user_id INTEGER, action TEXT, ts TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS comment_progress (user_id INTEGER PRIMARY KEY, photos INTEGER DEFAULT 0)')
    con.commit(); return con


def touch_user(user):
    con=db(); now=datetime.now(timezone.utc).isoformat()
    con.execute('INSERT INTO users VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,last_seen=excluded.last_seen',(user.id,user.username or '',now,now)); con.commit(); con.close()


def action(uid,name):
    con=db(); con.execute('INSERT INTO actions VALUES(?,?,?)',(uid,name,datetime.now(timezone.utc).isoformat())); con.commit(); con.close()


def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⚽ Удар по воротам',callback_data='game:football'),InlineKeyboardButton(text='🏀 Бросок в кольцо',callback_data='game:basketball')]])


def reward_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🎁 Посмотреть NFT',callback_data='nft:view')]])

def nft_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔗 Открыть NFT',url=NFT_LINK)], [InlineKeyboardButton(text='🎁 Забрать NFT',callback_data='nft:claim')]])

def comments_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='💬 Перейти к комментариям',callback_data='tasks:comments')]])


def tasks_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='1️⃣ Подпишись',url='https://t.me/hoqanft')],
        [InlineKeyboardButton(text='2️⃣ Лучший VPN',url=VPN_URL)],
        [InlineKeyboardButton(text='3️⃣ Подать заявку',url=APPLY_URL)],
        [InlineKeyboardButton(text='✅ Проверить',callback_data='tasks:check')],
    ])


@dp.message(CommandStart())
async def start(message: Message):
    touch_user(message.from_user)
    await message.answer_photo(FSInputFile(f'{IMG}/start.jpg'),caption='Испытайте удачу!\n\nВыберите, ударить по воротам или бросить мяч в кольцо, чтобы получить приз ⚽🏀',reply_markup=main_kb())


@dp.callback_query(F.data.startswith('game:'))
async def game(call: CallbackQuery):
    touch_user(call.from_user)
    sport=call.data.split(':',1)[1]
    action(call.from_user.id,f'game_{sport}')
    gif=f'{IMG}/{sport}.gif'
    label='Удар по воротам' if sport=='football' else 'Бросок в кольцо'
    await call.message.answer_animation(FSInputFile(gif),caption=f'{label} 🎯\n\n🎉 Вы попали!\n\nВам доступен NFT-приз. Выполните задания, чтобы получить его.',reply_markup=reward_kb())
    await call.answer()


@dp.callback_query(F.data=='nft:view')
async def nft_view(call: CallbackQuery):
    touch_user(call.from_user); action(call.from_user.id,'nft_view')
    link=NFT_LINK
    await call.message.answer_photo(FSInputFile(f'{IMG}/nft.jpg'),caption=f'🎁 Ваш NFT\n\nСсылка на коллекционный подарок:\n{link}\n\nНажмите «Забрать NFT», чтобы перейти к первому обязательному заданию.',reply_markup=nft_kb())
    await call.answer()


@dp.callback_query(F.data=='nft:claim')
async def nft_claim(call: CallbackQuery):
    touch_user(call.from_user); action(call.from_user.id,'nft_claim')
    await call.message.answer_photo(FSInputFile(f'{IMG}/comments.jpg'),caption='💬 Первое задание\n\nОставьте 10 комментариев под видео о подарках или звёздах в TikTok.\n\nТекст комментария:\n'+COMMENT_TEXT+'\n\nПоставьте лайк каждому комментарию и отправьте боту 10 скриншотов.\n\nПосле 10 скриншотов откроются остальные задания.',reply_markup=comments_kb())
    await call.answer()


@dp.callback_query(F.data=='tasks:open')
async def tasks_open(call: CallbackQuery):
    await call.message.answer_photo(FSInputFile(f'{IMG}/tasks.jpg'),caption='Отлично! Комментарии выполнены. Теперь доступны остальные задания.\n\nПосле выполнения нажмите ✅ Проверить.',reply_markup=tasks_kb()); await call.answer()


@dp.callback_query(F.data=='tasks:comments')
async def comments_task(call: CallbackQuery):
    touch_user(call.from_user); action(call.from_user.id,'comments_task')
    await call.message.answer_photo(FSInputFile(f'{IMG}/comments.jpg'),caption='Задание 2\n\nОставьте 10 комментариев под видео о подарках или звёздах в TikTok.\n\nТекст:\n'+COMMENT_TEXT+'\n\nПоставьте лайк каждому комментарию.\nОтправьте боту 10 скриншотов выполненного задания.',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⬅️ К заданиям',callback_data='tasks:open')]])); await call.answer()


@dp.message(F.photo)
async def screenshots(message: Message):
    touch_user(message.from_user)
    con=db(); row=con.execute('SELECT photos FROM comment_progress WHERE user_id=?',(message.from_user.id,)).fetchone(); count=(row[0] if row else 0)+1
    con.execute('INSERT INTO comment_progress(user_id,photos) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET photos=excluded.photos',(message.from_user.id,count)); con.commit(); con.close()
    if count<10:
        await message.answer(f'📸 Скриншот {count}/10 принят.')
    else:
        action(message.from_user.id,'comments_10_screenshots'); await message.answer_photo(FSInputFile(f'{IMG}/tasks.jpg'),caption='✅ 10 скриншотов получено!\n\nТеперь доступны остальные задания. Выполните их и нажмите «Проверить».',reply_markup=tasks_kb())


@dp.callback_query(F.data=='tasks:check')
async def tasks_check(call: CallbackQuery):
    touch_user(call.from_user)
    subscribed=False
    try:
        member=await bot.get_chat_member(CHANNEL,call.from_user.id); subscribed=member.status in {'member','administrator','creator'}
    except Exception: pass
    con=db(); photos=(con.execute('SELECT photos FROM comment_progress WHERE user_id=?',(call.from_user.id,)).fetchone() or [0])[0]; con.close()
    if not subscribed:
        await call.answer('Сначала подпишитесь на @hoqanft',show_alert=True); return
    if photos<10:
        await call.answer(f'Нужно отправить ещё {10-photos} скриншотов комментариев.',show_alert=True); return
    action(call.from_user.id,'tasks_verified')
    await call.message.answer_photo(FSInputFile(f'{IMG}/nft.jpg'),caption='✅ Задания выполнены.\n\nОжидайте выдачи NFT.')
    await call.answer()


@dp.message(Command('admin'))
async def admin(message: Message):
    if message.from_user.id!=ADMIN_ID: return
    con=db(); total=con.execute('SELECT COUNT(*) FROM users').fetchone()[0]; today=datetime.now(timezone.utc).date().isoformat(); today_count=con.execute('SELECT COUNT(*) FROM users WHERE substr(first_seen,1,10)=?',(today,)).fetchone()[0]; actions=con.execute('SELECT COUNT(*) FROM actions').fetchone()[0]; con.close()
    await message.answer(f'🛠 Админка\n\nПользователей всего: {total}\nНовых сегодня: {today_count}\nДействий всего: {actions}\n\nРассылка: /broadcast текст')


@dp.message(Command('broadcast'))
async def broadcast(message: Message):
    if message.from_user.id!=ADMIN_ID: return
    text=message.text.partition(' ')[2].strip()
    if not text: return await message.answer('Использование: /broadcast текст')
    con=db(); ids=[r[0] for r in con.execute('SELECT user_id FROM users')]; con.close(); sent=0
    for uid in ids:
        try: await bot.send_message(uid,text); sent+=1; await asyncio.sleep(.04)
        except Exception: pass
    await message.answer(f'Рассылка завершена: {sent}/{len(ids)}')


async def main(): await dp.start_polling(bot)
if __name__=='__main__': asyncio.run(main())
