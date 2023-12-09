import os

import telebot

from telebot import types
from algorithms import get_prediction

bot = telebot.TeleBot('6504447282:AAH2b86-jWK3MehFQHDb-Li6whYu-TUewVM')

mode_type=0
trade_code = ''


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    but1 = types.KeyboardButton("Краткосрочный")
    but2 = types.KeyboardButton("Среднесрочный")
    but3 = types.KeyboardButton("Долгосрочный")
    markup.add(but1)
    markup.add(but2)
    markup.add(but3)
    hello_mess = f"Привет, {message.from_user.first_name}! Меня зовут Nala, я искусственный интеллект, созданный для помощи инвесторам и трейдерам на московской бирже."
    bot.send_message(message.chat.id, hello_mess, parse_mode='html', reply_markup=markup)
    bot.send_message(message.chat.id,
                     f"Существует три основных вида торговли на бирже в зависимости от времени, которое проходит между покупкой и продажей ценных бумаг:\n"
                     f"1) краткосрочная - покупка-продажа в течении дня (скальпинг)\n"
                     f"2) среднесрочная - покупка-продажа в течении 1-2 месяцев\n"
                     f"3) долгосрочная - покупка-продажа более года\n"
                     f"Какой из вариантов подходит именно Вам?")
    bot.register_next_step_handler(message, on_click)

@bot.message_handler(commands=["Краткосрочный", "Среднесрочный", "Долгосрочный"])
def on_click(message):
    mode = {'Краткосрочный': 0,
            'Среднесрочный': 1,
            'Долгосрочный': 2}
    if message.text in mode.keys():
        bot.send_message(message.chat.id, "Отлично! Теперь введи тикер, по которому ты хочешь получить информацию",
                         parse_mode='html')
        global mode_type
        mode_type = mode[message.text]
        bot.register_next_step_handler(message, get_company_for_trade)
    else:
        bot.send_message(message.chat.id,
                         f"Нужно выбрать один из трех режимов, попробуй еще раз")
        bot.register_next_step_handler(message, on_click)


@bot.message_handler(content_types=["text"])
def get_company_for_trade(message):
    if message.text:
        with open("save_tickers.txt", "r") as file:
            lines = file.readlines()

        is_company_exist = False

        for line in lines:
            if f"'{message.text.strip().upper()}'," in line:
                is_company_exist = True
                break

        if is_company_exist:
            bot.send_message(message.chat.id, "Провожу анализ ценных бумаг...")
            global trade_code
            trade_code = message.text.strip().upper()
            get_predict(message)
            bot.register_next_step_handler(message, on_click)
        else:
            bot.send_message(message.chat.id,
                             f"Компания {message.text.strip()} пока недоступна. Попробуйте другой тикер")
            bot.register_next_step_handler(message, get_company_for_trade)


def get_predict(message):
    global mode_type, trade_code
    predict = get_prediction(trade_code, mode_type, message.from_user.id)
    if predict in [0, 1]:
        image_path='images/'+str(message.from_user.id)+'.jpg'
        img = open(image_path, 'rb')
        bot.send_photo(chat_id=message.chat.id,  photo=img)
        os.remove(image_path)
    # print(predict_list, mode)
    mode_list = ['краткосрочной', 'среднесрочной', 'долгосрочной']
    if predict == 0:
        bot.send_message(message.chat.id,
                         f"У компании {trade_code} в {mode_list[mode_type]} перспективе ценные бумаги сейчас дешевеют, предлагаю тебе продавать их активы.")
    elif predict == 1:
        bot.send_message(message.chat.id,
                         f"У компании {trade_code} в {mode_list[mode_type]} перспективе ценные бумаги сейчас дорожают, предлагаю тебе покупать их активы.")
    else:
        bot.send_message(message.chat.id,
                         f"При оценке компании {trade_code} в {mode_list[mode_type]} перспективе возникла ошибка, попробуй выбрать другую компанию.")


bot.polling(none_stop=True)
