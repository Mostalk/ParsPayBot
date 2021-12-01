import telebot
import time
import threading
from yoomoney import Client, Quickpay

bot = telebot.TeleBot("2127016903:AAGev4h29ECmkZ7xcTyq2kxG435zYs73KXs", parse_mode="MARKDOWN")
token = "41001565381812.CD4C81BABB16ABECCC797EC8FAA73F931D050EB817A0DABA66730A17CAF9B02341E07E1E22F8370DE105E5A0B555CAC16DA01C87C6D21BE64FEDE0EF43EA83486BE628B61D18847D28EF9C2768382596691ED4FBCACC723E81D167AF883ED1F3C0913AF7FBCEF9B533877AC9AF2647B96CDF9426BE6ED50D71DE4F6B455ADCE2"
label = str(time.time())
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
