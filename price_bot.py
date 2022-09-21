import logging
from aiogram import Bot, Dispatcher, executor, types
import os
import parser

API_TOKEN = os.environ['API_TOKEN']

# Configure logging3
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
priceParser = parser.PriceParser()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привіт!\nЯ PriceBot!\nЗгодуй мені посилання")


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply("Привіт!\nЯ помічник і зараз все розповім\n"
                        "Наразі, я вмію добувати та сортувати ціни з таких сайтів:\n"
                        "www.zara.com\nwww.oysho.com\n"
                        "Я створю для тебе список, який буде відсортований за мінімальною вартістю\n"
                        "Сподіваюсь я буду корисним. Чекаю на посилання!")

@dp.message_handler()
async def get_list(message: types.Message):
    await message.reply('Я вже в процесі ...')
    if not priceParser.is_valid(message.text):
        await message.reply('Посилання невірне, спробуй ще.')
    ready_list = priceParser.get_goods_list(message.text)
    format_list = ''
    for item in ready_list:
        format_list += (f"<b>Вартість:</b> {item['price_uah']} UAH\n<b>Країна:</b> {item['country']}\n<b>Посилання:</b> <a href='{item['url']}'>тут</a>\n\n")
    print(format_list)
    await message.reply(format_list, parse_mode='html')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)