import telebot

from telebot import types
from algorithms import get_prediction

bot = telebot.TeleBot('6504447282:AAH2b86-jWK3MehFQHDb-Li6whYu-TUewVM')


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    but1 = types.KeyboardButton("Краткосрочный")
    but2 = types.KeyboardButton("Среднесрочный")
    but3 = types.KeyboardButton("Долгосрочный")
    markup.add(but1)
    markup.add(but2)
    markup.add(but3)
    hello_mess = f"Привет, {message.from_user.first_name}! Я телеграм бот созданный для помощи инвесторам и трейдерам на московской бирже. Пожалуйста, выбери свой инвестиционный профиль."
    bot.send_message(message.chat.id, hello_mess, parse_mode='html', reply_markup=markup)
    bot.send_message(message.chat.id,
                     f"Существует три основных вида торговли на бирже в зависимости от времени, которое проходит между покупкой и продажей ценных бумаг:\n"
                     f"1) краткосрочная - покупка-продажа в течении дня (скальпинг)\n"
                     f"2) среднесрочная - покупка-продажа в течении 1-2 месяцев\n"
                     f"3) долгосрочная - покупка-продажа более года\n"
                     f"Какой из вариантов подходит именно Вам?")
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    mode = {'Краткосрочный': 0,
            'Среднесрочный': 1,
            'Долгосрочный': 2}
    if message.text in mode.keys():
        bot.send_message(message.chat.id, "Отлично! Теперь введи тикер, по которому ты хочешь получить информацию",
                         parse_mode='html')
        bot.register_next_step_handler(message, get_company_for_trade, mode[message.text])
    else:
        bot.send_message(message.chat.id,
                         f"Нужно выбрать один из трех режимов, попробуй еще раз")
        bot.register_next_step_handler(message, on_click)



@bot.message_handler(content_types=["text"], mode=["int"])
def trade_mode(message, mode):
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
            bot.register_next_step_handler(message, on_click)
            get_predict(message, message.text.strip().upper(), mode)
        else:
            bot.send_message(message.chat.id,
                             f"Компания {message.text.strip()} пока недоступна. Попробуйте другой тикер")
            bot.register_next_step_handler(message, get_company_for_trade(mode))

def get_predict(message, trade_code, mode):
    predict_list = get_prediction(trade_code)
    # print(predict_list, mode)
    mode_list = ['краткосрочной', 'среднесрочной', 'долгосрочной']
    if predict_list[mode] == 0:
        bot.send_message(message.chat.id,
                         f"У компании {trade_code} в {mode_list[mode]} перспективе ценные бумаги сейчас дешевеют, предлагаю тебе продавать их активы.")
    else:
        bot.send_message(message.chat.id,
                         f"У компании {trade_code} в {mode_list[mode]} перспективе ценные бумаги сейчас дорожают, предлагаю тебе покупать их активы.")
    # bot.reply_to(message, "All will be fine with this company. Just relax, man. from: SnoopDog")

@bot.message_handler(commands=["text"], mode=["int"])
def get_company_for_trade(message, mode):
    trade_mode(message, mode)


# def invest_mode(message):
#     bot.send_message(message.chat.id,
#                      f"Хм. Похоже, что-то пошло не так. Выбери другой режим, а я пока постараюсь исправить ошибку")
#     on_click(message)


bot.polling(none_stop=True)
