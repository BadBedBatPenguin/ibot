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


def admin(func):
    def wrapper(*args, **kwargs):
        if args:
            payload = args[0]
            if payload and (
                payload.from_user.id in settings.admin_settings.superusers
                or users_table.check_admin_status_for_user(payload.from_user.id)
            ):
                return func(*args, **kwargs)
            elif payload:
                chat_id = (
                    payload.chat.id
                    if isinstance(payload, telebot.types.Message)
                    else payload.message.chat.id
                )
                bot.send_message(
                    chat_id,
                    "У вас нет прав на это действие",
                )
                return
        else:
            return func(*args, **kwargs)

    return wrapper


@bot.message_handler(commands=["start"])
def send_start_message(message: telebot.types.Message) -> None:
    users_table.register_user(message)
    _start_menu(message, settings.user_settings.welcome_message)


@bot.message_handler(commands=["menu"])
def get_main_menu(message: telebot.types.Message) -> None:
    _start_menu(message, settings.user_settings.menu_message)


@bot.callback_query_handler(func=lambda call: call.data == "/start")
def back_to_main_menu(call: telebot.types.CallbackQuery) -> None:
    bot.delete_message(call.message.chat.id, call.message.message_id)
    _start_menu(call.message, settings.user_settings.menu_message)


def _start_menu(message: telebot.types.Message, text: str) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    for menu_text, callback_data in settings.user_settings.main_menu:
        button = telebot.types.InlineKeyboardButton(
            menu_text, callback_data=callback_data
        )
        markup.add(button)

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "get_items")
def categories(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(text, callback_data=callback_data)
        for text, callback_data in settings.user_settings.categories
    )
    back_button = telebot.types.InlineKeyboardButton("Назад", callback_data="/start")
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data in ["ipads", "macbooks", "apple_watch", "accessories"]
)
def subcategories(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(
            subcategory, callback_data=f"{call.data}:{subcategory}"
        )
        for subcategory in settings.common_settings.subcategories[call.data]
    )
    back_button = telebot.types.InlineKeyboardButton("Назад", callback_data="get_items")
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите подкатегорию", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "iphones")
def iphone_models(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(model.split(":")[-1], callback_data=model)
        for model in settings.common_settings.iphone_models
    )
    back_button = telebot.types.InlineKeyboardButton("Назад", callback_data="get_items")
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите модель", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data in settings.common_settings.all_subcategories
    or call.data in settings.common_settings.iphone_models
)
def get_items(call: telebot.types.CallbackQuery) -> None:
    category = call.data.split(":")[0]
    print(category)
    subcategory = call.data.split(":")[-1] if category != "iphones" else ""
    model = call.data.split(":")[-1] if category == "iphones" else ""
    items = items_table.get_items_obj_by_category_model_subcategory(
        category, model, subcategory
    )
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(
            f"Name: {item.name}\nDescription: {item.description}\nPrice: {item.price}",
            callback_data=f"item_{item._id}",
        )
        for item in items
    )
    back_button = telebot.types.InlineKeyboardButton("Назад", callback_data=category)
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите товар", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "item")
def get_item(call: telebot.types.CallbackQuery) -> None:
    item_id = call.data.split("_")[1]
    item = items_table.get_item_obj_by_id(item_id)
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        "Купить", callback_data=f"buy_{item._id}"
    )
    back_button = telebot.types.InlineKeyboardButton(
        "Назад", callback_data=f"{item.category}:{item.model or item.subcategory}"
    )
    markup.add(button, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    if item.photo:
        bot.send_photo(
            call.message.chat.id,
            item.photo,
            f"Имя: {item.name}\nОписание: {item.description}\nЦена: {item.price}",
            reply_markup=markup,
        )
    else:
        bot.send_message(
            call.message.chat.id,
            f"Имя: {item.name}\nОписание: {item.description}\nЦена: {item.price}",
            reply_markup=markup,
        )


# admin panel
@bot.message_handler(commands=["admin"])
@admin
def admin_panel(message: telebot.types.Message) -> None:
    _admin_panel(message)


def _admin_panel(message: telebot.types.Message) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        "Управление товарами", callback_data="items_management"
    )
    markup.add(button)

    bot.send_message(message.chat.id, "Админ панель", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "items_management")
@admin
def items_management(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(item[0], callback_data=item[1])
        for item in settings.admin_settings.items_management
    )
    back_button = telebot.types.InlineKeyboardButton("Назад", callback_data="/admin")
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "/admin")
@admin
def back_to_admin_panel(call: telebot.types.CallbackQuery) -> None:
    bot.delete_message(call.message.chat.id, call.message.message_id)
    _admin_panel(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "admin_iphones")
@admin
def admin_iphones(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(model, callback_data=f"admin_{model}")
        for model in settings.common_settings.iphone_models
    )
    back_button = telebot.types.InlineKeyboardButton(
        "Назад", callback_data="items_management"
    )
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите модель", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data
    in [f"admin_{model}" for model in settings.common_settings.iphone_models]
)
@admin
def admin_iphone_models(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(
            item[0],
            callback_data=item[1].format(
                category="iphones", model=call.data, subcategory=""
            ),
        )
        for item in settings.admin_settings.update_items
    )
    back_button = telebot.types.InlineKeyboardButton("Назад", callback_data="iphones")
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id, "Редактирование товаров", reply_markup=markup
    )


@bot.callback_query_handler(
    func=lambda call: call.data
    in ["admin_ipads", "admin_macbooks", "admin_apple_watch", "admin_accessories"]
)
@admin
def admin_choose_subcategory(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = (
        telebot.types.InlineKeyboardButton(item, callback_data=f"{call.data}:{item}")
        for item in settings.common_settings.subcategories[
            call.data.replace("admin_", "")
        ]
    )
    back_button = telebot.types.InlineKeyboardButton(
        "Назад", callback_data="items_management"
    )
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выберите подкатегорию", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data
    in [
        f"admin_{subcategory}"
        for subcategory in settings.common_settings.all_subcategories
    ]
)
@admin
def update_items(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    category = call.data.split(":")[0].replace("admin_", "")
    buttons = (
        telebot.types.InlineKeyboardButton(
            item[0],
            callback_data=item[1].format(
                category=category,
                model="",
                subcategory=call.data.split(":")[1],
            ),
        )
        for item in settings.admin_settings.update_items
    )
    back_button = telebot.types.InlineKeyboardButton("Назад", callback_data=category)
    markup.add(*buttons, back_button)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id, "Редактирование товаров", reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "add")
@admin
def add_item(call: telebot.types.CallbackQuery) -> None:
    category, model, subcategory = call.data.split("_")[1:]
    item = Item(category=category, model=model, subcategory=subcategory)
    msg = bot.send_message(call.message.chat.id, "Введите название товара")
    bot.register_next_step_handler(msg, save_item_name, item=item)


@admin
def save_item_name(message: telebot.types.Message, item: Item):
    item.name = message.text
    msg = bot.reply_to(message, "Введите описание товара")
    bot.register_next_step_handler(msg, save_item_description, item=item)


@admin
def save_item_description(message: telebot.types.Message, item: Item):
    item.description = message.text
    msg = bot.reply_to(message, "Приложите заглавное фото товара")
    bot.register_next_step_handler(msg, save_item_photo, item=item)


@admin
def save_item_photo(message: telebot.types.Message, item: Item):
    item.photo = message.photo[-1].file_id if message.photo else None
    msg = bot.reply_to(message, "Введите цену товара")
    bot.register_next_step_handler(msg, save_item_price, item=item)


@admin
def save_item_price(message: telebot.types.Message, item: Item):
    item.price = Decimal(message.text.strip().replace(",", "."))
    items_table.save_item(item)
    bot.send_message(message.from_user.id, f"Спасибо, сохранён товар:\n{item.dict()}")


@admin
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
@admin
def delete_item(call: telebot.types.CallbackQuery) -> None:
    item_id = call.data.split("_")[1]
    items_table.delete_item(item_id)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"Товар с id {item_id} удалён")


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "updateitems")
@admin
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
@admin
def update_item(call: telebot.types.CallbackQuery) -> None:
    item_id = call.data.split("_")[1]
    item = items_table.get_item_obj_by_id(item_id)

    msg = bot.send_message(
        call.message.chat.id,
        f"Текущее название товара: {item.name}\nВведите новое название товара или отправьте skip, чтобы оставить без изменений",
    )
    bot.register_next_step_handler(msg, update_item_name, item=item)


@admin
def update_item_name(message: telebot.types.Message, item: Item):
    item.name = message.text if message.text != "skip" else item.name
    msg = bot.reply_to(
        message,
        f"Текущее описание товара: {item.description}\nВведите новое описание товара или отправьте skip, чтобы оставить без изменений",
    )
    bot.register_next_step_handler(msg, update_item_description, item=item)


@admin
def update_item_description(message: telebot.types.Message, item: Item):
    item.description = message.text if message.text != "skip" else item.description
    msg = bot.reply_to(
        message,
        f"Текущая цена товара: {item.price}\nВведите новую цену товара или отправьте skip, чтобы оставить без изменений",
    )
    bot.register_next_step_handler(msg, update_item_price, item=item)


@admin
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


@bot.message_handler(commands=["make_admin"])
@admin
def make_admin(message: telebot.types.Message) -> None:
    if message.from_user.id not in settings.admin_settings.superusers:
        bot.send_message(message.chat.id, "У вас нет прав на это действие")
        return

    users_table.make_user_admin(message.text.split()[1])

    bot.send_message(
        message.chat.id,
        f"Пользователь {message.text.split()[1]} назначен администратором",
    )


@bot.message_handler(commands=["unmake_admin"])
@admin
def unmake_admin(message: telebot.types.Message) -> None:
    if message.from_user.id not in settings.admin_settings.superusers:
        bot.send_message(message.chat.id, "У вас нет прав на это действие")
        return

    users_table.unmake_user_admin(message.text.split()[1])

    bot.send_message(
        message.chat.id,
        f"Пользователь {message.text.split()[1]} больше не администратор",
    )


@bot.message_handler(commands=["get_all_admins"])
@admin
def get_all_admins_usernames(message: telebot.types.Message) -> None:
    if message.from_user.id not in settings.admin_settings.superusers:
        bot.send_message(message.chat.id, "У вас нет прав на это действие")
        return

    bot.send_message(
        message.chat.id,
        ", ".join(users_table.get_admins_usernames()),
    )


bot.polling(none_stop=True)
