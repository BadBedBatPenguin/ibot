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
    buyout_manager_message = (
        "Заявка на выкуп:\nПользователь: @{username}\nМодель устройства: {model}\nВизуальное состояние: {visual}"
        "\nЕсть ли у устройства технические проблемы: {issues}\nСостояние батареи: {battery}\nКомплектация к устройству: {equipment}"
    )
    fix_manager_message = "Заявка на ремонт:\nПользователь: @{username}\nМодель устройства: {model}\nНеисправность: {issue}"
    not_allowed_message = "У вас нет прав на это действие"
    create_item_form = [
        "Введите название товара",
        "Введите описание товара",
        "Приложите заглавное фото товара",
        "Введите ссылку на фотографии товара, или отправьте skip, если фотографий нет",
        "Введите цену товара",
    ]
    create_item_report = "Товар успешно добавлен"
    delete_item_report = "Товар успешно удалён"
    update_item_form = [
        "Текущее название товара: {name}\nВведите новое название товара или отправьте skip, чтобы оставить без изменений",
        "Текущее описание товара: {description}\nВведите новое описание товара или отправьте skip, чтобы оставить без изменений",
        "Текущее фото товара.\nПриложите новое фото товара или отправьте skip, чтобы оставить без изменений",
        "Текущие фото товара: {photos}\nВведите новую ссылку или отправьте skip, чтобы оставить без изменений",
        "Текущая цена товара: {price}\nВведите новую цену товара или отправьте skip, чтобы оставить без изменений",
    ]
    update_item_report = "Товар успешно изменён"
    make_admin_report = "Пользователь @{username} успешно назначен администратором"
    remove_admin_report = "Пользователь @{username} успешно удалён из администраторов"
    send_spam_form = ["Отправьте сообщение, которое хотели бы разослать"]
    send_spam_confirmation_question = "Это сообщение будет разослано всем юзерам, вы подтверждаете рассылку?"
    send_spam_report = "Рассылка завершена"


class UserSettings:
    main_menu = [
        ("Наличие 🔥", "categories"),
        ("Выкуп ♻️", "buyout"),
        ("Ремонт 🛠️", "fix"),
    ]
    welcome_message = "Приветственное письмо в котором говорится что чтобы открыть меню нужно ввести /menu и что заявка подтверждена"
    menu_message = "Главное меню"
    categories = [
        ("Айфоны", "iphones"),
        ("Айпады", "ipads"),
        ("Макбуки", "macbooks"),
        ("Apple watch", "apple_watch"),
        ("Аксессуары", "accessories"),
    ]
    buy_message_to_manager = "Сообщение о покупке"
    start_request_to_manager = (
        "Пользователь @{username} хочет вступить в группу с ботом. Принять запрос?"
    )
    buyout_form = [
        "Модель устройства",
        "Визуальное состояние",
        "Есть ли у устройства технические проблемы",
        "Состояние батареи",
        "Комплектация к устройству",
    ]
    fix_form = [
        "Модель устройства",
        "Неисправность",
    ]
    accept_form_report = "✅Ваша заявка принята, в ближайшее время с вами свяжется менеджер.\nБлагодарим за обращение ❤️"
    buy_report = "Ваш запрос на покупку товара принят.\nВаш товар:\n{name}\n{description}\n{price}"
    sign_up_report = "Ваш запрос на вступление в группу принят.\nОжидайте подтверждения от администратора"
    sign_up_rejected = "Ваш запрос на вступление в группу отклонён"


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
