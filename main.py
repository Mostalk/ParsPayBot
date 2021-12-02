import configparser
import os
import sys
import time

from telethon import TelegramClient, events, utils, Button
from telethon.tl.functions.messages import ExportChatInviteRequest
from yoomoney import Quickpay, Client

config = configparser.ConfigParser()
config.read('config.ini')
api_id = int(config['telegram']['api_id'])
api_hash = config['telegram']['api_hash']

client = TelegramClient('session_name', api_id, api_hash)
client.start()
bot = TelegramClient("bot", api_id, api_hash)
bot.start()
file = open("chats")
chats = list(map(lambda s: int(s.strip()), file.readlines()))
markup = [Button.text('Добавить канал'), Button.text('В работе')]
file.close()
yoo = Client(config['pay']['token'])


@bot.on(events.CallbackQuery())
async def handler_event(event):
    ename = event.data.decode("utf-8")
    if ename == "Добавить":
        mess = await bot.get_messages(event.original_update.user_id, ids=event.original_update.msg_id)
        async for dialog in client.iter_dialogs():
            if dialog.title == mess.text:
                f = open("chats", "a")
                f.write(f"{dialog.id}\n")
                f.close()
        await bot.send_message("mostalik", mess.text + " добавлен", buttons=[Button.text("Сохранить")])
    elif ename == "Удалить":
        mess = await bot.get_messages(event.original_update.user_id, ids=event.original_update.msg_id)
        async for dialog in client.iter_dialogs():
            if dialog.title == mess.text:
                f = open("chats", "r")
                rows = f.readlines()
                rows.remove(f"{dialog.id}\n")
                f.close()
                f = open("chats", "w")
                for row in rows:
                    f.write(row)
                f.close()
        await bot.send_message("mostalik", mess.text + " добавлен", buttons=[Button.text("Сохранить")])


@bot.on(events.NewMessage(incoming=True))
async def handler_start(event):
    if event.text == "/start":
        if event.chat_id != 0:
            label = str(time.time())
            await bot.send_message(event.chat_id, "Здравствуйте, Вам нужно оплатить доступ к каналу")
            quickpay = Quickpay(
                receiver="41001565381812",
                quickpay_form="shop",
                targets="Оплата доступа",
                paymentType="SB",
                sum=100,
                label=label
            )
            peer = await client.get_input_entity("Test channel")
            invite = await client(ExportChatInviteRequest(
                peer=peer,
                usage_limit=1,
            ))
            await bot.send_message(event.chat_id, "Ссылка для опалаты:\n" + quickpay.base_url)
            print("Checking payment...")
            history = yoo.operation_history(label=label)
            while not len(history.operations):
                time.sleep(2)
                history = yoo.operation_history(label=label)
            for operation in history.operations:
                print()
                print("Operation:", operation.operation_id)
                print("\tStatus     -->", operation.status)
            await bot.send_message(event.chat_id, "Оплата получена\nВаша уникальная ссылка\n" + invite.link)

        await bot.send_message(event.chat_id, "Добро пожаловать в бота", buttons=markup)
    if event.text == "Добавить канал":
        async for dialog in client.iter_dialogs():
            if dialog.is_channel and not dialog.is_group:
                await bot.send_message(event.chat_id, dialog.title, buttons=[Button.inline('Добавить')])
    if event.text == "В работе":
        for dialog in open("chats").readlines():
            ent = await client.get_entity(int(dialog.strip()))
            if hasattr(ent, "title"):
                await bot.send_message(event.chat_id, ent.title, buttons=[Button.inline('Удалить')])
            else:
                name = ent.first_name + " " + "" if not ent.last_name else ent.last_name
                await bot.send_message(event.chat_id, name, buttons=[Button.inline('Удалить')])
    if event.text == "Сохранить":
        await bot.send_message(event.chat_id, "Сохранено", buttons=markup)
        os.startfile(__file__)
        sys.exit()
    if event.message.forward:
        f = open("chats", "a")
        f.write(f"{event.message.forward.chat_id}\n")
        f.close()
        await bot.send_message(event.chat_id, f"{event.message.forward.chat.title}  добавлен", buttons=markup)
        os.startfile(__file__)
        sys.exit()


@client.on(events.NewMessage(chats=chats))
async def handler_all(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    msg_id = event.id

    sender = await event.get_sender()
    name = utils.get_display_name(sender)

    chat_from = event.chat if event.chat else (await event.get_chat())
    chat_title = utils.get_display_name(chat_from)

    await client.send_message("Test channel", f"**{chat_title}**:\n\n{event.text}", parse_mode='md', buttons=markup)
    print(f"ID: {chat_id} {chat_title} >>  (ID: {sender_id})  {name} - (ID: {msg_id}) {event.text}")


with client:
    client.run_until_disconnected()
