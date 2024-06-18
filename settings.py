class AdminSettings:
    categories = [
        ("Айфоны", "admin_iphones"),
        ("Айпады", "admin_ipads"),
        ("Макбуки", "admin_macbooks"),
        ("Apple watch", "admin_apple_watch"),
        ("Аксессуары", "admin_accessories"),
    ]
    admin_menu = [
        ("Добавить товар", "add_{category}_{model}_{subcategory}"),
        ("Удалить товар", "deleteitems_{category}_{model}_{subcategory}"),
        ("Изменить товар", "updateitems_{category}_{model}_{subcategory}"),
    ]
    items_actions = [
        ("Добавить товар", "add"),
        ("Удалить товар", "delete"),
        ("Изменить товар", "update"),
    ]

    superusers = [629909066]
    manager_chat_id = 629909066


class UserSettings:
    main_menu = [
        ("Товары", "categories"),
        ("Выкуп", "buyout"),
        ("Ремонт", "fix"),
    ]
    welcome_message = "Приветственное письмо"
    menu_message = "Главное меню"
    categories = [
        ("Айфоны", "iphones"),
        ("Айпады", "ipads"),
        ("Макбуки", "macbooks"),
        ("Apple watch", "apple_watch"),
        ("Аксессуары", "accessories"),
    ]
    buy_message_to_manager = "Сообщение о покупке"


class CommonSettings:
    categories = [
        ("Айфоны", "models", "iphones"),
        ("Айпады", "items", "ipads"),
        ("Макбуки", "items", "macbooks"),
        ("Apple watch", "items", "apple_watch"),
        ("Аксессуары", "subcategories", "accessories"),
    ]
    accessories = [
        ("Зарядки", "chargers"),
        ("Чехлы", "cases"),
        ("Наушники", "headphones"),
        ("Защитные стекла", "protection_glasses"),
        ("Прочее", "other"),
    ]
    iphone_models = [
        "iPhone X",
        "iPhone XR",
        "iPhone XS",
        "iPhone XS Max",
        "iPhone 11",
        "iPhone 11 Pro",
        "iPhone 11 Pro Max",
        "iPhone 12",
        "iPhone 12 mini",
        "iPhone 12 Pro",
        "iPhone 12 Pro Max",
        "iPhone 13",
        "iPhone 13 mini",
        "iPhone 13 Pro",
        "iPhone 13 Pro Max",
        "iPhone 14",
        "iPhone 14 Plus",
        "iPhone 14 Pro",
        "iPhone 14 Pro Max",
        "iPhone 15",
        "iPhone 15 Plus",
        "iPhone 15 Pro",
        "iPhone 15 Pro Max",
    ]
    # iphone_models = [(model, f"iphones:{model}") for model in iphone_models]
    default_photo = ""
    categories_without_subcategory = ["ipads", "macbooks", "apple_watch"]

    @property
    def accessory_subcategories(self) -> list[str]:
        return [f"accessories:{subcategory}" for _, subcategory in self.accessories]


admin_settings = AdminSettings()
user_settings = UserSettings()
common_settings = CommonSettings()
