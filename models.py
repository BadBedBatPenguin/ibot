import telebot

from database.models import Item
from settings import admin_settings, common_settings, user_settings


class CallBackData:
    def __init__(
        self,
        admin: bool | None = None,
        action: str | None = None,
        category: str | None = None,
        subcategory: str | None = None,
        model: str | None = None,
        item_id: str | None = None,
        user_id: str | None = None,
        from_str: str | None = None,
    ) -> None:
        if from_str:
            data = from_str.split(":")
            self.admin = data[0] == "True"
            self.action = data[1]
            self.category = data[2] if data[2] else None
            self.subcategory = data[3] if data[3] else None
            self.model = data[4] if data[4] else None
            self.item_id = data[5] if data[5] else None
            self.user_id = data[6] if data[6] else None
            return
        self.admin = admin
        self.action = action
        self.category = category if category else ""
        self.subcategory = subcategory if subcategory else ""
        self.model = model if model else ""
        self.item_id = item_id if item_id else ""
        self.user_id = user_id if user_id else ""

    def str(self) -> str:
        return f"{self.admin}:{self.action}:{self.category}:{self.subcategory}:{self.model}:{self.item_id}:{self.user_id}"


class Menu:
    title: str
    action: str
    admin: bool
    buttons: list
    prev_action: str | None


class AdminMainMenu(Menu):
    def __init__(self) -> None:
        self.title = admin_settings.main_menu_title
        self.admin = True
        self.action = "main_menu"
        self.prev_action = None
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                name, callback_data=CallBackData(admin=True, action=action).str()
            )
            for name, action in admin_settings.main_menu
        ]


class UserMainMenu(Menu):
    def __init__(self) -> None:
        self.title = user_settings.main_menu_title
        self.admin = False
        self.action = "start"
        self.prev_action = None
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                name,
                callback_data=CallBackData(admin=False, action=action).str(),
            )
            for name, action in user_settings.main_menu
        ]


class Categories(Menu):
    def __init__(self, admin: bool) -> None:
        self.title = common_settings.categories_menu_title
        self.action = "categories"
        self.prev_action = "main_menu" if admin else "start"
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                name,
                callback_data=CallBackData(
                    admin=admin, action=action, category=category
                ).str(),
            )
            for name, action, category in common_settings.categories
        ]
        self.buttons.append(
            telebot.types.InlineKeyboardButton(
                common_settings.back_button_text,
                callback_data=CallBackData(admin=admin, action=self.prev_action).str(),
            )
        )
        self.admin = admin


class IphonesModels(Menu):
    def __init__(self, admin: bool, models_to_show: list[str] | str = "all") -> None:
        self.title = common_settings.models_menu_title
        self.action = "models"
        self.admin = admin
        self.prev_action = "categories"
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                model,
                callback_data=CallBackData(
                    admin=admin, action="items", category="iphones", model=model
                ).str(),
            )
            for model in common_settings.iphone_models
            if models_to_show == "all" or model in models_to_show
        ]
        self.buttons.append(
            telebot.types.InlineKeyboardButton(
                common_settings.back_button_text,
                callback_data=CallBackData(admin=admin, action=self.prev_action).str(),
            )
        )


class Subcategories(Menu):
    def __init__(
        self, admin: bool, category: str, subcategories_to_show: list[str] | str = "all"
    ) -> None:
        self.title = common_settings.subcategories_menu_title
        self.action = "subcategories"
        self.admin = admin
        self.prev_action = "categories"
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                name,
                callback_data=CallBackData(
                    admin=admin,
                    action="items",
                    category=category,
                    subcategory=subcategory,
                ).str(),
            )
            for name, subcategory in common_settings.accessories
            if subcategories_to_show == "all" or subcategory in subcategories_to_show
        ]
        self.buttons.append(
            telebot.types.InlineKeyboardButton(
                common_settings.back_button_text,
                callback_data=CallBackData(
                    admin=admin, action=self.prev_action, category=category
                ).str(),
            )
        )


class Items(Menu):
    def __init__(
        self,
        admin: bool,
        category: str,
        subcategory: str | None = None,
        model: str | None = None,
        items: list | None = None,
    ) -> None:
        self.action = "items"
        self.admin = admin
        if model:
            self.prev_action = "models"
        elif subcategory:
            self.prev_action = "subcategories"
        else:
            self.prev_action = "categories"
        if admin:
            self.title = admin_settings.items_menu_title
            self.buttons = [
                telebot.types.InlineKeyboardButton(
                    name,
                    callback_data=CallBackData(
                        admin=admin,
                        action=action,
                        category=category,
                        subcategory=subcategory,
                        model=model,
                    ).str(),
                )
                for name, action in admin_settings.items_actions
            ]
        else:
            self.title = user_settings.items_menu_title
            self.buttons = [
                telebot.types.InlineKeyboardButton(
                    f"{item.name} {item.price}",
                    callback_data=CallBackData(
                        admin=admin,
                        action="item_info",
                        item_id=item._id,
                    ).str(),
                )
                for item in items
            ]
        self.buttons.append(
            telebot.types.InlineKeyboardButton(
                "Назад",
                callback_data=CallBackData(
                    admin=admin,
                    action=self.prev_action,
                    category=category,
                    subcategory=subcategory,
                    model=model,
                ).str(),
            )
        )


class ItemView(Menu):
    def __init__(self, item: Item) -> None:
        self.action = "item_info"
        self.admin = False
        self.prev_action = "items"
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                user_settings.buy_button_text,
                callback_data=CallBackData(
                    admin=self.admin,
                    action="buy",
                    item_id=item._id,
                ).str(),
            ),
            telebot.types.InlineKeyboardButton(
                common_settings.back_button_text,
                callback_data=CallBackData(
                    admin=self.admin,
                    action=self.prev_action,
                    category=item.category,
                    subcategory=item.subcategory,
                    model=item.model,
                ).str(),
            ),
        ]


class DeleteItems(Menu):
    def __init__(
        self,
        items: list[Item],
        category: str,
        subcategory: str | None = None,
        model: str | None = None,
    ) -> None:
        self.action = "deleteitem"
        self.admin = True
        self.prev_action = "items"
        self.title = admin_settings.delete_menu_title
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                admin_settings.item_button_text.format(
                    name=item.name,
                    price=item.price,
                ),
                callback_data=CallBackData(
                    admin=self.admin,
                    action=self.action,
                    item_id=item._id,
                ).str(),
            )
            for item in items
        ]
        self.buttons.append(
            telebot.types.InlineKeyboardButton(
                common_settings.back_button_text,
                callback_data=CallBackData(
                    admin=self.admin,
                    action=self.prev_action,
                    category=category,
                    subcategory=subcategory,
                    model=model,
                ).str(),
            )
        )


class UpdateItems(Menu):
    def __init__(
        self,
        items: list[Item],
        category: str,
        subcategory: str | None = None,
        model: str | None = None,
    ) -> None:
        self.action = "updateitem"
        self.admin = True
        self.prev_action = "items"
        self.title = admin_settings.update_menu_title
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                admin_settings.item_button_text.format(
                    name=item.name,
                    price=item.price,
                ),
                callback_data=CallBackData(
                    admin=self.admin,
                    action=self.action,
                    item_id=item._id,
                ).str(),
            )
            for item in items
        ]
        self.buttons.append(
            telebot.types.InlineKeyboardButton(
                "Назад",
                callback_data=CallBackData(
                    admin=self.admin,
                    action=self.prev_action,
                    category=category,
                    subcategory=subcategory,
                    model=model,
                ).str(),
            )
        )


class StartRequest(Menu):
    def __init__(self, user: telebot.types.User) -> None:
        self.action = "start_request"
        self.admin = True
        self.prev_action = None
        self.title = user_settings.start_request_to_manager.format(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self.buttons = [
            telebot.types.InlineKeyboardButton(
                admin_settings.accept_button_text,
                callback_data=CallBackData(
                    admin=self.admin,
                    action="accept_request",
                    user_id=user.id,
                ).str(),
            ),
            telebot.types.InlineKeyboardButton(
                admin_settings.reject_button_text,
                callback_data=CallBackData(
                    admin=self.admin,
                    action="reject_request",
                    user_id=user.id,
                ).str(),
            ),
        ]
