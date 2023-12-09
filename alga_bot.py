import os
import json
import telebot

from telebot import types
from algorithms import get_prediction

bot = telebot.TeleBot('6986377523:AAFIcc-iDKEnE6S-r0lP-XQSvHkCXuBOjvQ')

mode_type=0
company_data = []


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    but1 = types.KeyboardButton("Краткосрочный")
    but2 = types.KeyboardButton("Среднесрочный")
    but3 = types.KeyboardButton("Долгосрочный")
    markup.add(but1)
    markup.add(but2)
    markup.add(but3)
    hello_mess = f"Привет, {message.from_user.first_name}!\n"
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
        bot.send_message(message.chat.id, "Отлично! Теперь введите тикер, или название компании, для которой Вы хотите получить информацию. "
                                          "Например: SBER (Сбербанк), LKOH (Лукойл), GAZP (Газпром)...",
                         parse_mode='html')
        global mode_type
        mode_type = mode[message.text]
        bot.register_next_step_handler(message, get_company_for_trade)
    else:
        bot.send_message(message.chat.id,
                         f"Нужно выбрать один из трех режимов, попробуйте еще раз.")
        bot.register_next_step_handler(message, on_click)


@bot.message_handler(content_types=["text"])
def get_company_for_trade(message):
    if message.text:
        global company_data
        company_data = get_company_or_tiket_data(message.text)
        if company_data:
            bot.send_message(message.chat.id, f"Было выбрано: {company_data} \n")
            bot.send_message(message.chat.id, "Провожу анализ ценных бумаг...")
            get_predict(message, company_data[0])
            bot.register_next_step_handler(message, start)
        else:
            bot.send_message(message.chat.id,
                             f"Тикет/компания {message.text.strip()} пока недоступа. Попробуйте ввести название на другом языке."
                             f"Например: SBER (Сбербанк), LKOH (Лукойл), GAZP (Газпром)...")
            bot.register_next_step_handler(message, get_company_for_trade)

def get_company_or_tiket_data(search_text):
    #return list [trade_code, INSTRUMENT_TYPE, EMITENT_FULL_NAME]
    trade_code = ''
    with open('trade_data.json', 'r', encoding='utf-8') as file:
        trade_data = json.load(file)
        if search_text.strip().upper() in trade_data.keys():
            trade_code = search_text.strip().upper()
        else:
            for key in trade_data.keys():
                if search_text.strip().upper() in trade_data[key]['EMITENT_FULL_NAME'].upper():
                    trade_code = key
                    break
    if trade_code != '':
        company_data = [trade_code, trade_data[trade_code]['INSTRUMENT_TYPE'], trade_data[trade_code]['EMITENT_FULL_NAME']]
    else:
        company_data = []
    return company_data

def get_predict(message, trade_code):
    global mode_type
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
