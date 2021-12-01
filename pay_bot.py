import telebot
import time
import threading
import configparser
from yoomoney import Client, Quickpay

config = configparser.ConfigParser()
config.read('config.ini')
bot = telebot.TeleBot(config['pay']['token'], parse_mode="MARKDOWN")
token = label = str(time.time())
client = Client(token)


def check_pay(lab, uid):
    print("Checking payment...")
    history = client.operation_history(label=lab)
    while not len(history.operations):
        time.sleep(1)
        history = client.operation_history(label=lab)
    for operation in history.operations:
        print()
        print("Operation:", operation.operation_id)
        print("\tStatus     -->", operation.status)
    bot.send_message(uid, "Оплата успешна. Я съебую")


@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(message.chat.id, "Здравствуйте, Вам нужно оплатить доступ к каналу")
    quickpay = Quickpay(
        receiver="41001565381812",
        quickpay_form="shop",
        targets="Оплата доступа",
        paymentType="SB",
        sum=100,
        label=label
    )
    print(quickpay.base_url)

    bot.send_message(message.chat.id, "Ссылка для опалаты:\n" + quickpay.base_url)
    threading.Thread(target=check_pay, args=[label, message.chat.id]).start()


bot.infinity_polling(skip_pending=True)
