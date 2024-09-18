import os


class AdminSettings:
    superusers = [629909066]
    manager_chat_id = 629909066 if os.environ.get("LOCAL") else 6967930534
    manager_username = (
        "Badbedbatpenguin" if os.environ.get("LOCAL") else "TechnoHub_manager"
    )

    main_menu = [
        ("Управление товарами", "categories"),
        ("Сделать рассылку", "send_spam"),
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

    main_menu_title = "Админская панель"
    items_menu_title = "Редактирование товаров"
    delete_menu_title = "Какой товар удалить?"
    item_button_text = "{name} {price}"
    update_menu_title = "Какой товар изменить?"
    accept_button_text = "Принять"
    reject_button_text = "Отклонить"
    buyout_manager_message = (
        "Заявка на выкуп:\nПользователь: @{username}\nМодель устройства: {model}\nОпишите визуальное состояние устройства: {visual}"
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
    send_spam_confirmation_question = 'Это сообщение будет разослано всем юзерам, вы подтверждаете рассылку?(отправьте "да" или "нет")'
    send_spam_report = "Рассылка завершена"
    buy_message_to_manager = (
        "Заявка на покупку:\nПользователь: @{username}\nКатегория: {category}\nПодкатегория: {subcategory}"
        "\nМодель: {model}\nНазвание: {name}\nЦена: {price}\nДополнительные аксессуары: {accessories}"
    )


class UserSettings:
    main_menu = [
        ("Наличие 🔥", "categories"),
        ("Выкуп ♻️", "buyout"),
        ("Ремонт 🛠️", "fix"),
    ]
    welcome_message = (
        "Добро пожаловать в TehnoHub !\n\n"
        "Телеграм-бот, в котором Вы сможете решить любой вопрос касающийся техники Apple\n\n"
        "Вы можете интересующую вас категорию ниже👇"
    )
    welcome_photo_item_id = "790d8cc3-f6bc-4170-8e66-fc73add55443"
    main_menu_title = "Главное меню"
    items_menu_title = "Выберите товар"
    buy_button_text = "Купить"
    start_request_to_manager = "Пользователь @{username} ({first_name}, {last_name}) хочет вступить в группу с ботом. Принять запрос?"
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
    buy_report = "Ваш запрос на покупку товара принят.\nС вами свяжется менеджер для уточнения деталей @{manager_username}"
    sign_up_report = "Ваш запрос на вступление в группу принят.\nОжидайте подтверждения от администратора"
    sign_up_rejected = "Ваш запрос на вступление в группу отклонён"
    buy_iphone_menu_title = (
        "Хотите добавить аксессуары к покупке ❓"
    )
    case = "Чехол"
    glass = "Стекло"
    charger = "Блок питания"
    add_accessories_buttons_names = {
        "case": "Чехол",
        "glass": "Стекло",
        "charger": "Блок питания",
    }
    add_accessories_buttons = {
        "unchecked": {
            "case": f"⬜️{add_accessories_buttons_names['case']}",
            "glass": f"⬜️{add_accessories_buttons_names['glass']}",
            "charger": f"⬜️{add_accessories_buttons_names['charger']}",
        },
        "checked": {
            "case": f"✅{add_accessories_buttons_names['case']}",
            "glass": f"✅{add_accessories_buttons_names['glass']}",
            "charger": f"✅{add_accessories_buttons_names['charger']}",
        },
    }
    buy_iphone_accept_button_name = "Подтвердить"


class CommonSettings:
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
    default_photo = ""
    categories_without_subcategory = ["ipads", "macbooks", "apple_watch"]
    categories_menu_title = "Выберите категорию"
    back_button_text = "Назад"
    models_menu_title = "Выберите модель"
    subcategories_menu_title = "Выберите подкатегорию"
    error_message = "Произошла ошибка"
    default_hyperlink_text = "Смотреть фото 📸"

    @property
    def accessory_subcategories(self) -> list[str]:
        return [f"accessories:{subcategory}" for _, subcategory in self.accessories]


class CategoriesSettings:
    iphone_category_name = "iPhone"
    ipad_category_name = "iPad"
    macbook_category_name = "MacBook"
    apple_watch_category_name = "Apple Watch"
    accessories_category_name = "Аксессуары"
    categories = [
        (iphone_category_name, "models", "iphones"),
        (ipad_category_name, "items", "ipads"),
        (macbook_category_name, "items", "macbooks"),
        (apple_watch_category_name, "items", "apple_watch"),
        (accessories_category_name, "subcategories", "accessories"),
    ]


admin_settings = AdminSettings()
user_settings = UserSettings()
common_settings = CommonSettings()
categories_settings = CategoriesSettings()
