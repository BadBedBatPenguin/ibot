import os

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
                    settings.admin_settings.not_allowed_message,
                )
                return
        else:
            return func(*args, **kwargs)

    return wrapper


@bot.message_handler(commands=["start"])
def send_start_message(message: telebot.types.Message) -> None:
    if not users_table.is_registered(message.from_user.id):
        users_table.register_user(
            _id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    _start_menu(message.chat.id, True)


@bot.message_handler(commands=["menu"])
def get_main_menu(message: telebot.types.Message) -> None:
    _start_menu(message.chat.id, False)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "start"
    and not models.CallBackData(from_str=call.data).admin
)
def back_to_main_menu(call: telebot.types.CallbackQuery) -> None:
    bot.delete_message(call.message.chat.id, call.message.message_id)
    _start_menu(call.message.chat.id, False)


def _start_menu(chat_id: str, welcome: bool) -> None:
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.UserMainMenu()
    markup.add(*menu.buttons)

    if os.environ.get("LOCAL"):
        bot.send_message(
            chat_id,
            settings.user_settings.welcome_message if welcome else menu.title,
            reply_markup=markup,
        )
    else:
        photo_item = items_table.get_item_obj_by_id(
            settings.user_settings.welcome_photo_item_id
        )
        bot.send_photo(
            chat_id,
            photo_item.photo,
            settings.user_settings.welcome_message if welcome else menu.title,
            reply_markup=markup,
        )


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
        admin=False,
        category=models.CallBackData(from_str=call.data).category,
        subcategories_to_show=items_table.not_empty_subcategories(),
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
    menu = models.IphonesModels(
        admin=False, models_to_show=items_table.not_empty_models()
    )
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
            parse_mode="HTML",
            reply_markup=markup,
        )
    else:
        bot.send_message(
            call.message.chat.id,
            str(item),
            parse_mode="HTML",
            reply_markup=markup,
        )


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "buy"
    and not models.CallBackData(from_str=call.data).admin
)
def buy_item(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    item = items_table.get_item_obj_by_id(callback_data.item_id)
    if callback_data.accessories:
        case, glass, charger = tuple(callback_data.accessories.split())
        accessories = []
        if case == "1":
            accessories.append(settings.user_settings.case)
        if glass == "1":
            accessories.append(settings.user_settings.glass)
        if charger == "1":
            accessories.append(settings.user_settings.charger)
    else:
        accessories = None
    bot.send_message(
        settings.admin_settings.manager_chat_id,
        settings.admin_settings.buy_message_to_manager.format(
            username=call.message.chat.username,
            category=item.category,
            subcategory=item.subcategory,
            model=item.model,
            name=item.name,
            price=item.price,
            accessories=", ".join(accessories) if accessories else "нет",
        ),
    )
    bot.send_message(
        call.message.chat.id,
        settings.user_settings.buy_report.format(
            manager_username=settings.admin_settings.manager_username
        ),
    )


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action
    == "buy_iphone_menu"
    and not models.CallBackData(from_str=call.data).admin
)
def buy_iphone_menu(call: telebot.types.CallbackQuery) -> None:
    callback_data = models.CallBackData(from_str=call.data)
    if callback_data.accessories is None:
        accessories = {
            "case": False,
            "glass": False,
            "charger": False,
        }
    else:
        accessories_str: list[str] = callback_data.accessories.split()
        accessories = {
            "case": accessories_str[0] == "1",
            "glass": accessories_str[1] == "1",
            "charger": accessories_str[2] == "1",
        }
    markup = telebot.types.InlineKeyboardMarkup()
    menu = models.BuyIphone(callback_data.item_id, **accessories)
    markup.add(*menu.buttons)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, menu.title, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: models.CallBackData(from_str=call.data).action == "buyout"
    and not models.CallBackData(from_str=call.data).admin
)
def buyout(call: telebot.types.CallbackQuery) -> None:
    form = {"username": call.message.chat.username}
    msg = bot.send_message(call.message.chat.id, settings.user_settings.buyout_form[0])
    bot.register_next_step_handler(msg, get_model_name, form=form)


def get_model_name(message: telebot.types.Message, form: dict):
    form["model"] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[1])
    bot.register_next_step_handler(msg, get_visual_state, form=form)


def get_visual_state(message: telebot.types.Message, form: dict):
    form["visual"] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[2])
    bot.register_next_step_handler(msg, get_issues, form=form)


def get_issues(message: telebot.types.Message, form: dict):
    form["issues"] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[3])
    bot.register_next_step_handler(msg, get_battery_state, form=form)


def get_battery_state(message: telebot.types.Message, form: dict):
    form["battery"] = message.text
    msg = bot.reply_to(message, settings.user_settings.buyout_form[4])
    bot.register_next_step_handler(msg, get_equipment, form=form)


def get_equipment(message: telebot.types.Message, form: dict):
    form["equipment"] = message.text
    bot.send_message(
        settings.admin_settings.manager_chat_id,
        settings.admin_settings.buyout_manager_message.format(**form),
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
    form = {"username": call.message.chat.username}
    msg = bot.send_message(call.message.chat.id, settings.user_settings.fix_form[0])
    bot.register_next_step_handler(msg, fix_form_get_model_name, form=form)


def fix_form_get_model_name(message: telebot.types.Message, form: dict):
    form["model"] = message.text
    msg = bot.reply_to(message, settings.user_settings.fix_form[1])
    bot.register_next_step_handler(msg, fix_form_get_problem, form=form)


def fix_form_get_problem(message: telebot.types.Message, form: dict):
    form["issue"] = message.text
    bot.send_message(
        settings.admin_settings.manager_chat_id,
        settings.admin_settings.fix_manager_message.format(**form),
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
    msg = bot.send_message(
        call.message.chat.id, settings.admin_settings.create_item_form[0]
    )
    bot.register_next_step_handler(msg, save_item_name, item=item)


@admin
def save_item_name(message: telebot.types.Message, item: Item):
    item.name = message.text
    msg = bot.reply_to(message, settings.admin_settings.create_item_form[1])
    bot.register_next_step_handler(msg, save_item_description, item=item)


@admin
def save_item_description(message: telebot.types.Message, item: Item):
    item.description = message.text
    msg = bot.reply_to(message, settings.admin_settings.create_item_form[2])
    bot.register_next_step_handler(msg, save_item_photo, item=item)


@admin
def save_item_photo(message: telebot.types.Message, item: Item):
    item.photo = message.photo[-1].file_id if message.photo else None
    msg = bot.reply_to(
        message,
        settings.admin_settings.create_item_form[3],
    )
    bot.register_next_step_handler(msg, save_item_photos, item=item)


@admin
def save_item_photos(message: telebot.types.Message, item: Item):
    if message.text == "skip":
        item.photos = None
    elif "text_link" in [entity.type for entity in message.entities]:
        entity = [entity for entity in message.entities if entity.type == "text_link"][
            0
        ]
        item.photos = {
            "url": entity.url,
            "text": message.text,
        }
    else:
        item.photos["url"] = message.text

    msg = bot.reply_to(message, settings.admin_settings.create_item_form[4])
    bot.register_next_step_handler(msg, save_item_price, item=item)


@admin
def save_item_price(message: telebot.types.Message, item: Item):
    item.price = message.text if message.text != "skip" else None
    saved = items_table.save_item(item)
    if saved:
        bot.send_message(
            message.from_user.id, settings.admin_settings.create_item_report
        )
    else:
        bot.send_message(message.from_user.id, settings.common_settings.error_message)


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
    bot.send_message(call.message.chat.id, settings.admin_settings.delete_item_report)


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
        settings.admin_settings.update_item_form[0].format(name=item.name),
    )
    bot.register_next_step_handler(msg, update_item_name, item=item)


@admin
def update_item_name(message: telebot.types.Message, item: Item):
    item.name = message.text if message.text != "skip" else item.name
    msg = bot.reply_to(
        message,
        settings.admin_settings.update_item_form[1].format(
            description=item.description
        ),
    )
    bot.register_next_step_handler(msg, update_item_description, item=item)


@admin
def update_item_description(message: telebot.types.Message, item: Item):
    item.description = message.text if message.text != "skip" else item.description
    msg = bot.send_photo(
        message.chat.id,
        item.photo,
        caption=settings.admin_settings.update_item_form[2],
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
        settings.admin_settings.update_item_form[3].format(photos=item.photos_str()),
        parse_mode="HTML",
    )
    bot.register_next_step_handler(msg, update_item_photos, item=item)


@admin
def update_item_photos(message: telebot.types.Message, item: Item):
    if message.text == "skip":
        item.photos = item.photos
    elif "text_link" in [entity.type for entity in message.entities]:
        entity = [entity for entity in message.entities if entity.type == "text_link"][
            0
        ]
        item.photos = {
            "url": entity.url,
            "text": message.text,
        }
    else:
        item.photos = {"url": message.text}
    msg = bot.reply_to(
        message,
        settings.admin_settings.update_item_form[4].format(price=item.price),
    )
    bot.register_next_step_handler(msg, update_item_price, item=item)


@admin
def update_item_price(message: telebot.types.Message, item: Item):
    item.price = message.text if message.text != "skip" else item.price
    items_table.edit_item(item._id, item.dict())
    bot.send_message(message.from_user.id, settings.admin_settings.update_item_report)


@bot.message_handler(commands=["make_admin"])
@admin
def make_admin(message: telebot.types.Message) -> None:
    username = message.text.split()[1]
    if message.from_user.id not in settings.admin_settings.superusers:
        bot.send_message(message.chat.id, settings.admin_settings.not_allowed_message)
        return

    users_table.make_user_admin(username)

    bot.send_message(
        message.chat.id,
        settings.admin_settings.make_admin_report.format(username=username),
    )


@bot.message_handler(commands=["unmake_admin"])
@admin
def unmake_admin(message: telebot.types.Message) -> None:
    username = message.text.split()[1]
    if message.from_user.id not in settings.admin_settings.superusers:
        bot.send_message(message.chat.id, settings.admin_settings.not_allowed_message)
        return

    users_table.unmake_user_admin(username)

    bot.send_message(
        message.chat.id,
        username,
    )


@bot.message_handler(commands=["get_all_admins"])
@admin
def get_all_admins_usernames(message: telebot.types.Message) -> None:
    if message.from_user.id not in settings.admin_settings.superusers:
        bot.send_message(message.chat.id, settings.admin_settings.not_allowed_message)
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
        call.message.chat.id, settings.admin_settings.send_spam_form[0]
    )
    bot.register_next_step_handler(msg, send_spam_message)


@admin
def send_spam_message(message: telebot.types.Message) -> None:
    msg = bot.send_message(
        message.chat.id,
        settings.admin_settings.send_spam_confirmation_question,
    )
    bot.register_next_step_handler(msg, send_spam_confirmation, message.text)


@admin
def send_spam_confirmation(message: telebot.types.Message, text: str) -> None:
    if message.text.lower() == "да":
        users = users_table.get_all_users_ids()
        for user in users:
            bot.send_message(user, text)

        bot.send_message(message.chat.id, settings.admin_settings.send_spam_report)
    else:
        _admin_panel(message)


@bot.chat_join_request_handler()
def join_request(message: telebot.types.Message) -> None:
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)
    if not users_table.is_registered(message.from_user.id):
        users_table.register_user(
            _id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    _start_menu(message.from_user.id, True)


@bot.chat_member_handler()
def left_chat(update: telebot.types.ChatMemberUpdated) -> None:
    if update.difference.get("status", (None, None))[1] in ["kicked", "left"]:
        users_table.delete_user(update.old_chat_member.user.id)


bot.polling(none_stop=True)
