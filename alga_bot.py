import telebot

from telebot import types
from algorithms import get_prediction

bot = telebot.TeleBot('6504447282:AAH2b86-jWK3MehFQHDb-Li6whYu-TUewVM')


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    but1 = types.KeyboardButton("Долгосрочный")
    but2 = types.KeyboardButton("Краткосрочный")
    markup.add(but1, but2)
    hello_mess = f"Привет, {message.from_user.first_name}! Я телеграм бот созданный для помощи инвесторам и трейдерам на московской бирже. Пожалуйста, выбери свой инвестиционный профиль"
    bot.send_message(message.chat.id, hello_mess, parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == 'Долгосрочный':
        bot.send_message(message.chat.id,
                         f"Хм. Похоже, что-то пошло не так. Выбери другой режим, а я пока постараюсь исправить ошибку")
        bot.register_next_step_handler(message, on_click)
        # bot.register_next_step_handler(message, invest_mode)
    elif message.text == 'Краткосрочный':
        bot.send_message(message.chat.id, "Отлично! Теперь введи тикер, по которому ты хочешь получить информацию",
                         parse_mode='html')
        bot.register_next_step_handler(message, get_company_for_trade)
        # bot.register_next_step_handler(message, trade_mode)
    else:
        bot.send_message(message.chat.id,
                         f"Нужно выбрать один из двух режимов")
        bot.register_next_step_handler(message, on_click)
        # return 0


@bot.message_handler(content_types=["text"])
def trade_mode(message):
    if message.text:
        with open("save_tickers.txt", "r") as file:
            lines = file.readlines()

        is_company_exist = False

        for line in lines:
            if f"'{message.text.strip().upper()}'," in line:
                is_company_exist = True
                get_predict(message, message.text.strip().upper())
                break
        if is_company_exist == False:
            bot.send_message(message.chat.id, f"Компания {message.text.strip()} пока недоступна. Попробуйте другой тикер")
            bot.register_next_step_handler(message, get_company_for_trade)
        if is_company_exist:
            bot.send_message(message.chat.id, "End...")
            bot.register_next_step_handler(message, on_click)


def get_predict(message, trade_code):
    get_prediction(trade_code)
    # bot.reply_to(message, "All will be fine with this company. Just relax, man. from: SnoopDog")

@bot.message_handler(commands=["text"])
def get_company_for_trade(message):
    trade_mode(message)


# def invest_mode(message):
#     bot.send_message(message.chat.id,
#                      f"Хм. Похоже, что-то пошло не так. Выбери другой режим, а я пока постараюсь исправить ошибку")
#     on_click(message)


bot.polling(none_stop=True)
