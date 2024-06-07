class AdminSettings:
    items_management = [
        ("Айфоны", "iphones"),
        ("Айпады", "ipads"),
        ("Макбуки", "macbooks"),
        ("Часы Apple", "apple_watch"),
        ("Аксессуары", "accessories"),
    ]
    iphone_models = ["12", "13", "14", "15"]
    update_items = [
        ("Добавить товар", "add_{category}_{model}_{subcategory}"),
        ("Удалить товар", "deleteitems_{category}_{model}_{subcategory}"),
        ("Изменить товар", "updateitems_{category}_{model}_{subcategory}"),
    ]
    subcategories = {
        "ipads": ["air", "mini", "pro"],
        "macbooks": ["air", "pro"],
        "apple_watch": ["series_3", "series_4", "series_5", "series_6", "series_7"],
        "accessories": ["cases", "chargers", "headphones", "cables"],
    }

    @property
    def all_subcategories(self) -> list[str]:
        return [
            f"{category}:{subcategory}"
            for category in self.subcategories
            for subcategory in self.subcategories[category]
        ]


admin_settings = AdminSettings()
