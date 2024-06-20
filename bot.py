import json
import os
from decimal import Decimal

import dns.resolver
import telebot

import models
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
    if not users_table.is_registered(message.from_user.id):
        menu = models.StartRequest(user=message.from_user)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(*menu.buttons)
        bot.send_message(
            settings.admin_settings.manager_chat_id,
            menu.title,
            reply_markup=markup,
        )
        bot.send_message(
            message.chat.id,
            "Ваш запрос на встепление в группу принят.\nОжидайте подтверждения от администратора",
        )
    else:
        _start_menu(message.chat.id, settings.user_settings.menu_message)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "accept_request"
    and models.CallBackData(from_str=call.data).admin
)
def accept_start_request(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    users_table.register_user(call.message)
    _start_menu(callback_data.user_id, settings.user_settings.welcome_message)
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "reject_request"
    and models.CallBackData(from_str=call.data).admin
)
def reject_start_request(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    bot.send_message(
        callback_data.user_id, "Ваш запрос на вступление в группу отклонён"
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(commands=["menu"])
def get_main_menu(message: telebot.types.Message) -> None:
    _start_menu(message.chat.id, settings.user_settings.menu_message)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "start"
    and not models.CallBackData(from_str=call.data).admin
)
def back_to_main_menu(call: telebot.types.CallbackQuery) -> None:
    bot.delete_message(call.message.chat.id, call.message.message_id)
    _start_menu(call.message.chat.id, settings.user_settings.menu_message)


def _start_menu(chat_id: str, text: str) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.UserMainMenu()
    markup.add(*menu.buttons)

    bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "categories"
    and not models.CallBackData(from_str=call.data).admin
)
def categories(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.Categories(admin=False)
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "subcategories"
    and not models.CallBackData(from_str=call.data).admin
)
def accessories_subcategories(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.Subcategories(
        admin=False, category=models.CallBackData(from_str=call.data).category
    )
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "models"
    and not models.CallBackData(from_str=call.data).admin
)
def iphone_models(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.IphonesModels(admin=False)
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "items"
    and not models.CallBackData(from_str=call.data).admin
)
def get_items(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    items = items_table.get_items_obj_by_category_model_subcategory(
        callback_data.category, callback_data.model, callback_data.subcategory
    )
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.Items(
        admin=False,
        category=callback_data.category,
        model=callback_data.model,
        subcategory=callback_data.subcategory,
        items=items,
    )
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "item_info"
    and not models.CallBackData(from_str=call.data).admin
)
def get_item(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    item = items_table.get_item_obj_by_id(callback_data.item_id)
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.ItemView(item)
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    if item.photo:
        bot.send_photo(
            call.message.chat.id,
            item.photo,
            str(item),
            reply_markup=markup,
        )
    else:
        bot.send_message(
            call.message.chat.id,
            str(item),
            reply_markup=markup,
        )


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "buy"
    and not models.CallBackData(from_str=call.data).admin
)
def buy_item(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    item = items_table.get_item_obj_by_id(callback_data.item_id)
    bot.send_message(
        settings.admin_settings.manager_chat_id,
        settings.user_settings.buy_message_to_manager,
    )
    bot.send_message(
        call.message.chat.id,
        f"Ваш запрос на покупку товара принят.\nВаш товар:\n{item.name}\n{item.description}\n{item.price}",
    )


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "buyout"
    and not models.CallBackData(from_str=call.data).admin
)
def buyout(call: telebot.types.CallbackQuery) -> None:
    form = {"Пользователь": f"@{call.message.chat.username}"}
    msg = bot.send_message(call.message.chat.id, settings.user_settings.buyout_form[0])
    bot.register_next_step_handler(msg, get_model_name, form=form)


def get_model_name(message: telebot.types.Message, form: dict):
    form[settings.user_settings.buyout_form[0]] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[1])
    bot.register_next_step_handler(msg, get_visual_state, form=form)


def get_visual_state(message: telebot.types.Message, form: dict):
    form[settings.user_settings.buyout_form[1]] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[2])
    bot.register_next_step_handler(msg, get_technical_problems, form=form)


def get_technical_problems(message: telebot.types.Message, form: dict):
    form[settings.user_settings.buyout_form[2]] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[3])
    bot.register_next_step_handler(msg, get_battery_state, form=form)


def get_battery_state(message: telebot.types.Message, form: dict):
    form[settings.user_settings.buyout_form[3]] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[4])
    bot.register_next_step_handler(msg, get_equipment, form=form)


def get_equipment(message: telebot.types.Message, form: dict):
    form[settings.user_settings.buyout_form[4]] = message.text
    bot.send_message(
        settings.admin_settings.manager_chat_id,
        json.dumps(form, ensure_ascii=False),
    )
    bot.send_message(
        message.chat.id,
        settings.user_settings.accept_form_report,
    )


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "fix"
    and not models.CallBackData(from_str=call.data).admin
)
def fix(call: telebot.types.CallbackQuery) -> None:
    form = {"Пользователь": f"@{call.message.chat.username}"}
    msg = bot.send_message(call.message.chat.id, settings.user_settings.fix_form[0])
    bot.register_next_step_handler(msg, fix_form_get_model_name, form=form)


def fix_form_get_model_name(message: telebot.types.Message, form: dict):
    form[settings.user_settings.fix_form[0]] = message.text
    msg = bot.reply_to(message, settings.user_settings.fix_form[1])
    bot.register_next_step_handler(msg, fix_form_get_problem, form=form)


def fix_form_get_problem(message: telebot.types.Message, form: dict):
    form[settings.user_settings.fix_form[1]] = message.text
    bot.send_message(
        settings.admin_settings.manager_chat_id,
        json.dumps(form, ensure_ascii=False),
    )
    bot.send_message(
        message.chat.id,
        settings.user_settings.accept_form_report,
    )


# admin panel
@bot.message_handler(commands=["admin"])
@admin
def admin_panel(message: telebot.types.Message) -> None:
    _admin_panel(message)


def _admin_panel(message: telebot.types.Message) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.AdminMainMenu()
    markup.add(*menu.buttons)
    bot.send_message(message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "categories"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def admin_categories(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.Categories(admin=True)
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "main_menu"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def back_to_admin_panel(call: telebot.types.CallbackQuery) -> None:
    bot.delete_message(call.message.chat.id, call.message.message_id)
    _admin_panel(call.message)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "models"
    and models.CallBackData(from_str=call.data).admin
    and models.CallBackData(from_str=call.data).category == "iphones"
)
@admin
def admin_iphone_models(call: telebot.types.CallbackQuery) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.IphonesModels(admin=True)
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "items"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def admin_item_menu(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.Items(
        admin=True,
        category=callback_data.category,
        model=callback_data.model,
        subcategory=callback_data.subcategory,
    )
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "subcategories"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def admin_choose_subcategory(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.Subcategories(admin=True, category=callback_data.category)
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "add"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def add_item(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    item = Item(
        category=callback_data.category,
        model=callback_data.model,
        subcategory=callback_data.subcategory,
    )
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
    msg = bot.reply_to(
        message,
        "Введите ссылку на фотографии товара, или отправьте skip, если фотографий нет",
    )
    bot.register_next_step_handler(msg, save_item_photos, item=item)


@admin
def save_item_photos(message: telebot.types.Message, item: Item):
    item.photos = message.text if message.text != "skip" else None
    msg = bot.reply_to(message, "Введите цену товара")
    bot.register_next_step_handler(msg, save_item_price, item=item)


@admin
def save_item_price(message: telebot.types.Message, item: Item):
    item.price = Decimal(message.text.strip().replace(",", "."))
    items_table.save_item(item)
    bot.send_message(message.from_user.id, f"Спасибо, сохранён товар:\n{item.dict()}")


@admin
@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "delete"
    and models.CallBackData(from_str=call.data).admin
)
def delete_items(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    items = items_table.get_items_obj_by_category_model_subcategory(
        callback_data.category, callback_data.model, callback_data.subcategory
    )
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.DeleteItems(
        items, callback_data.category, callback_data.subcategory, callback_data.model
    )
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "deleteitem"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def delete_item(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    items_table.delete_item(callback_data.item_id)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"Товар с id {callback_data.item_id} удалён")


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "update"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def uppdate_items(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    items = items_table.get_items_obj_by_category_model_subcategory(
        callback_data.category, callback_data.model, callback_data.subcategory
    )
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.UpdateItems(
        items, callback_data.category, callback_data.subcategory, callback_data.model
    )
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "updateitem"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def update_item(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    item = items_table.get_item_obj_by_id(callback_data.item_id)

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
    msg = bot.send_photo(
        message.chat.id,
        item.photo,
        caption="Текущее фото товара.\nПриложите новое фото товара или отправьте skip, чтобы оставить без изменений",
        reply_to_message_id=message.message_id,
    )
    bot.register_next_step_handler(msg, update_item_photo, item=item)


@admin
def update_item_photo(message: telebot.types.Message, item: Item):
    item.photo = (
        message.photo[-1].file_id
        if (message.photo and message.text != "skip")
        else item.photo
    )
    msg = bot.reply_to(
        message,
        f"Текущие фото товара: {item.photos}\nВведите новую ссылку или отправьте skip, чтобы оставить без изменений",
    )
    bot.register_next_step_handler(msg, update_item_photos, item=item)


@admin
def update_item_photos(message: telebot.types.Message, item: Item):
    item.photos = message.text if message.text != "skip" else item.photos
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


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "send_spam"
    and models.CallBackData(from_str=call.data).admin
)
@admin
def send_spam(call: telebot.types.CallbackQuery) -> None:
    msg = bot.send_message(
        call.message.chat.id, "Отправьте сообщение, которое хотели бы разослать"
    )
    bot.register_next_step_handler(msg, send_spam_message)


@admin
def send_spam_message(message: telebot.types.Message) -> None:
    msg = bot.send_message(
        message.chat.id,
        "Это сообщение будет разослано всем юзерам, вы подтверждаете рассылку?",
    )
    bot.register_next_step_handler(msg, send_spam_confirmation, message.text)


@admin
def send_spam_confirmation(message: telebot.types.Message, text: str) -> None:
    if message.text.lower() == "да":
        users = users_table.get_all_users_ids()
        for user in users:
            bot.send_message(user, text)

        bot.send_message(message.chat.id, "Рассылка завершена")
    else:
        _admin_panel(message)


bot.polling(none_stop=True)
