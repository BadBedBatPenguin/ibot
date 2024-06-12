class AdminSettings:
    items_management = [
        ("Айфоны", "admin_iphones"),
        ("Айпады", "admin_ipads"),
        ("Макбуки", "admin_macbooks"),
        ("Часы Apple", "admin_apple_watch"),
        ("Аксессуары", "admin_accessories"),
    ]
    update_items = [
        ("Добавить товар", "add_{category}_{model}_{subcategory}"),
        ("Удалить товар", "deleteitems_{category}_{model}_{subcategory}"),
        ("Изменить товар", "updateitems_{category}_{model}_{subcategory}"),
    ]

    superusers = [629909066]
    manager_chat_id = 629909066


class UserSettings:
    main_menu = [
        ("Товары", "get_items"),
        ("Выкуп", "buyout"),
        ("Ремонт", "fix"),
    ]
    welcome_message = "Приветственное письмо"
    menu_message = "Главное меню"
    categories = [
        ("Айфоны", "iphones"),
        ("Айпады", "ipads"),
        ("Макбуки", "macbooks"),
        ("Часы Apple", "apple_watch"),
        ("Аксессуары", "accessories"),
    ]
    buy_message_to_manager = "Сообщение о покупке"


class CommonSettings:
    subcategories = {
        "ipads": ["air", "mini", "pro"],
        "macbooks": ["air", "pro"],
        "apple_watch": ["series_3", "series_4", "series_5", "series_6", "series_7"],
        "accessories": ["cases", "chargers", "headphones", "cables"],
    }
    iphone_models_names = ["12", "13", "14", "15"]
    iphone_models = [f"iphones:{model}" for model in iphone_models_names]
    default_photo = ""

    @property
    def all_subcategories(self) -> list[str]:
        return [
            f"{category}:{subcategory}"
            for category in self.subcategories
            for subcategory in self.subcategories[category]
        ]


admin_settings = AdminSettings()
user_settings = UserSettings()
common_settings = CommonSettings()
