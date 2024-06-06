import os

import dns.resolver
import telebot

from database.database import DataBase

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8"]

bot = telebot.TeleBot(os.environ.get("TOKEN"))
print(os.environ.get("MONGO_USERNAME"))
database = DataBase(
    connection_string=f"mongodb+srv://{os.environ.get('MONGO_USERNAME')}:{os.environ.get('MONGO_PASSWORD')}@cluster0.4v7iiok.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    db_name=os.environ.get("DB_NAME"),
)


@bot.message_handler(commands=["start"])
def send_start_message(message):
    database.register_user(message)
    bot.send_message(message.chat.id, "Какое-то стартовое сообщение")


@bot.message_handler(commands=["sub"])
def send_sub(message):
    database.subscribe_user(message)
    bot.send_message(message.chat.id, "Ты подписан")


@bot.message_handler(commands=["unsub"])
def send_unsub(message):
    database.unsubscribe_user(message)
    bot.send_message(message.chat.id, "Ты отписан, лох")


@bot.message_handler(commands=["get_all_users_identificators"])
def test1(message):
    msg = " ".join(map(str, database.get_all_users_identificators()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["get_all_users"])
def test2(message):
    msg = " ".join(map(str, database.get_all_users_data()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["get_subscribed_users_data"])
def test10(message):
    msg = " ".join(map(str, database.get_subscribed_users_data()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["get_subscribed_users_identificators"])
def test15(message):
    msg = " ".join(map(str, database.get_subscribed_users_identificators()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["check_my_status"])
def test3(message):
    bot.send_message(
        message.from_user.id,
        database.check_subscription_status_for_user(message.chat.id),
    )


@bot.message_handler(commands=["stats"])
def test4(message):
    bot.send_message(message.from_user.id, str(database.get_subscription_stats()))


bot.polling(none_stop=True)
