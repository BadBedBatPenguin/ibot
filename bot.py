import os
from decimal import Decimal

import dns.resolver
import telebot

import settings
from database.database import Items, Users
from database.models import Item

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8"]

bot = telebot.TeleBot(os.environ.get("TOKEN"))
users_table = Users(
    connection_string=f"mongodb+srv://{os.environ.get('MONGO_USERNAME')}:{os.environ.get('MONGO_PASSWORD')}@cluster0.4v7iiok.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    db_name=os.environ.get("DB_NAME"),
)
items_table = Items(
    connection_string=f"mongodb+srv://{os.environ.get('MONGO_USERNAME')}:{os.environ.get('MONGO_PASSWORD')}@cluster0.4v7iiok.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    db_name=os.environ.get("DB_NAME"),
)


@bot.message_handler(commands=["start"])
def send_start_message(message):
    users_table.register_user(message)
    bot.send_message(message.chat.id, "Какое-то стартовое сообщение")


@bot.message_handler(commands=["sub"])
def send_sub(message):
    users_table.subscribe_user(message)
    bot.send_message(message.chat.id, "Ты подписан")


@bot.message_handler(commands=["unsub"])
def send_unsub(message):
    users_table.unsubscribe_user(message)
    bot.send_message(message.chat.id, "Ты отписан, лох")


@bot.message_handler(commands=["get_all_users_identificators"])
def test1(message):
    msg = " ".join(map(str, users_table.get_all_users_identificators()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["get_all_users"])
def test2(message):
    msg = " ".join(map(str, users_table.get_all_users_data()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["get_subscribed_users_data"])
def test10(message):
    msg = " ".join(map(str, users_table.get_subscribed_users_data()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["get_subscribed_users_identificators"])
def test15(message):
    msg = " ".join(map(str, users_table.get_subscribed_users_identificators()))
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=["check_my_status"])
def test3(message):
    bot.send_message(
        message.from_user.id,
        users_table.check_subscription_status_for_user(message.chat.id),
    )


@bot.message_handler(commands=["stats"])
def test4(message):
    bot.send_message(message.from_user.id, str(users_table.get_subscription_stats()))


@bot.message_handler(commands=["admin"])
def admin_panel(message: telebot.types.Message) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        "Управление товарами", callback_data="items_management"
    )
    markup.add(button)

    bot.send_message(message.chat.id, "Админ панель", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "items_management")
def items_management(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(item[0], callback_data=item[1])
        for item in settings.admin_settings.items_management
    )
    markup.add(*buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "iphones")
def iphones(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(model, callback_data=model)
        for model in settings.admin_settings.iphone_models
    )
    markup.add(*buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите модель", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data in settings.admin_settings.iphone_models
)
def iphone(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(
            item[0],
            callback_data=item[1].format(
                category="iphone", model=call.data, subcategory=""
            ),
        )
        for item in settings.admin_settings.update_items
    )
    markup.add(*buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id, "Редактирование товаров", reply_markup=markup
    )


@bot.callback_query_handler(
    func=lambda call: call.data in ["ipads", "macbooks", "apple_watch", "accessories"]
)
def choose_category(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(item, callback_data=f"{call.data}:{item}")
        for item in settings.admin_settings.subcategories[call.data]
    )
    markup.add(*buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите подкатегорию", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data in settings.admin_settings.all_subcategories
)
def update_items(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(
            item[0],
            callback_data=item[1].format(
                category=call.data.split(":")[0],
                model="",
                subcategory=call.data.split(":")[1],
            ),
        )
        for item in settings.admin_settings.update_items
    )
    markup.add(*buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id, "Редактирование товаров", reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "add")
def add_item(call: telebot.types.CallbackQuery) -> None:
    print(f"creating item for {call.data}")
    category, model, subcategory = call.data.split("_")[1:]
    item = Item(category=category, model=model, subcategory=subcategory)
    print(item.dict())
    msg = bot.send_message(call.message.chat.id, "Введите название товара")
    bot.register_next_step_handler(msg, save_item_name, item=item)


def save_item_name(message: telebot.types.Message, item: Item):
    item.name = message.text
    print(item.dict())
    msg = bot.reply_to(message, "Введите описание товара")
    bot.register_next_step_handler(msg, save_item_description, item=item)


def save_item_description(message: telebot.types.Message, item: Item):
    item.description = message.text
    print(item.dict())
    msg = bot.reply_to(message, "Введите цену товара")
    bot.register_next_step_handler(msg, save_item_price, item=item)


def save_item_price(message: telebot.types.Message, item: Item):
    item.price = Decimal(message.text.strip().replace(",", "."))
    print(item.dict())
    items_table.save_item(item)
    bot.send_message(message.from_user.id, f"Спасибо, сохранён товар:\n{item.dict()}")


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "deleteitems")
def delete_items(call: telebot.types.CallbackQuery) -> None:
    category, model, subcategory = call.data.split("_")[1:]
    items = items_table.get_items_obj_by_category_model_subcategory(
        category, model, subcategory
    )
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(
            f"Name: {item.name}\nDescription: {item.description}\nPrice: {item.price}",
            callback_data=f"deleteitem_{item._id}",
        )
        for item in items
    )
    markup.add(*buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Какой товар удалить?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "deleteitem")
def delete_item(call: telebot.types.CallbackQuery) -> None:
    item_id = call.data.split("_")[1]
    items_table.delete_item(item_id)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"Товар с id {item_id} удалён")


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "updateitems")
def uppdate_items(call: telebot.types.CallbackQuery) -> None:
    category, model, subcategory = call.data.split("_")[1:]
    items = items_table.get_items_obj_by_category_model_subcategory(
        category, model, subcategory
    )
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(
            f"Name: {item.name}\nDescription: {item.description}\nPrice: {item.price}",
            callback_data=f"updateitem_{item._id}",
        )
        for item in items
    )
    markup.add(*buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Какой товар изменить?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "updateitem")
def update_item(call: telebot.types.CallbackQuery) -> None:
    item_id = call.data.split("_")[1]
    item = items_table.get_item_obj_by_id(item_id)

    msg = bot.send_message(
        call.message.chat.id,
        f"Текущее название товара: {item.name}\nВведите новое название товара или отправьте skip, чтобы оставить без изменений",
    )
    bot.register_next_step_handler(msg, update_item_name, item=item)


def update_item_name(message: telebot.types.Message, item: Item):
    item.name = message.text if message.text != "skip" else item.name
    msg = bot.reply_to(
        message,
        f"Текущее описание товара: {item.description}\nВведите новое описание товара или отправьте skip, чтобы оставить без изменений",
    )
    bot.register_next_step_handler(msg, update_item_description, item=item)


def update_item_description(message: telebot.types.Message, item: Item):
    item.description = message.text if message.text != "skip" else item.description
    msg = bot.reply_to(
        message,
        f"Текущая цена товара: {item.price}\nВведите новую цену товара или отправьте skip, чтобы оставить без изменений",
    )
    bot.register_next_step_handler(msg, update_item_price, item=item)


def update_item_price(message: telebot.types.Message, item: Item):
    item.price = (
        Decimal(message.text.strip().replace(",", "."))
        if message.text != "skip"
        else item.price
    )
    items_table.edit_item(item._id, item.dict())
    bot.send_message(
        message.from_user.id, f"Спасибо, сохранёны изменения:\n{item.dict()}"
    )


bot.polling(none_stop=True)
