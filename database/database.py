from pymongo import MongoClient

from database.models import Item


class DataBase:
    """
    - register_user(message)
    - subscribe_user(message)
    - unsubscribe_user(message)
    - check_subscription_status_for_user(user_id)
    - get_all_users_data()
    - get_subscribed_users_data()
    - get_all_users_identificators()
    - get_subscribed_users_identificators()
    - get_subscription_stats()
    """

    def __init__(self, connection_string, db_name):
        self._cluster = MongoClient(connection_string)
        self._db = self._cluster[db_name]

        self._db_name = db_name

        print("db inited successfully")


class Users(DataBase):
    def __init__(self, connection_string, db_name):
        super().__init__(connection_string, db_name)

        self._collection = self._db["users"]

    def register_user(self, message):
        """
        register user in the colelction[users] in the format:
        {
            '_id': message.from_user.id,
            'username': message.chat.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'is_admin': False,
        }
        """
        try:
            # if user is not registered
            if self._collection.count_documents({"_id": message.from_user.id}) == 0:
                self._collection.insert_one(
                    {
                        "_id": message.from_user.id,
                        "username": message.chat.username,
                        "first_name": message.from_user.first_name,
                        "last_name": message.from_user.last_name,
                        "is_admin": False,
                    }
                )

            return True

        except Exception as error:
            # return False if operation is not done
            print(error)
            return False

    def make_user_admin(self, username: str) -> bool | str:
        """
        make user admmin
        if user is not in the collection, return error message
        if user is alreary in the collection, change user field "is_admin" = True
        """
        if username.startswith("@"):
            username = username[1:]
        try:
            # return error if user is not in collection
            if self._collection.count_documents({"username": username}) == 0:
                return f"User with username: {username} is not in the database."
            # update user status if user is in collection
            else:
                self._collection.update_one(
                    {"username": username},
                    {
                        "$set": {"is_admin": True},
                    },
                )

            # return True if operation is done
            return True

        except Exception as error:
            # return False if operation is not done
            print(error)
            return False

    def unmake_user_admin(self, username: str) -> bool | str:
        """
        unmake user admmin
        if user is not in the collection, return error message
        if user is alreary in the collection, change user field "is_admin" = False
        """
        if username.startswith("@"):
            username = username[1:]
        try:
            # return error if user is not in collection
            if self._collection.count_documents({"username": username}) == 0:
                return f"User with username: {username} is not in the database."
            # update user status if user is in collection
            else:
                self._collection.update_one(
                    {"username": username},
                    {
                        "$set": {"is_admin": False},
                    },
                )

            # return True if operation is done
            return True

        except Exception as error:
            # return False if operation is not done
            print(error)
            return False

    def check_subscription_status_for_user(self, user_id):
        """
        Check user subscription status;
        return True/False values;
        """
        try:
            return self._collection.find_one({"_id": user_id})["isSubscribed"]

        except Exception as error:
            print(error)

    def get_all_users_data(self):
        """
        return users list with all data from collection[users]
        list(dict(), dict(), dict(),...)
        """
        try:
            return list(self._collection.find())

        except Exception as error:
            print(error)

    def get_admins_usernames(self):
        """
        return users list with usernames from collection[users] for admins [is_admin == True]
        list[str]
        """
        try:
            users = self._collection.find({"is_admin": True})
            return [f"@{user['username']}" for user in users]

        except Exception as error:
            print(error)

    def check_admin_status_for_user(self, user_id):
        """
        Check user admin status;
        return True/False values;
        """
        try:
            return self._collection.find_one({"_id": user_id})["is_admin"]

        except Exception as error:
            print(error)


class Items(DataBase):
    def __init__(self, connection_string, db_name):
        super().__init__(connection_string, db_name)

        self._collection = self._db["items"]

    def save_item(self, item: Item) -> bool:
        """
        save item in the colelction[items] in the format:
         {
             '_id': item.id,
             'name': item.name,
             'description': item.description,
             'category': item.category,
             'subcategory': item.subcategory,
             'model': item.model,
             'price': item.price,
         }
        """
        try:
            # if item has not been saved before
            if self._collection.count_documents({"_id": item._id}) == 0:
                self._collection.insert_one(item.dict())
            # if item already exists
            else:
                print(
                    f"Item with id: {item._id} already exists in the collection[items]."
                )

            # return True if operation is done
            return True

        except Exception as error:
            # return False if operation is not done
            print(error)
            return False

    def edit_item(self, id: str, data: dict) -> bool:
        """
        edit item in the collection[items]
        if item is not in the collection, add item
        """
        try:
            # add item if item is not in collection
            if self._collection.count_documents({"_id": id}) == 0:
                item = Item(**data, _id=id)
                self._collection.insert_one(item.dict())
            # update item if item is in collection
            else:
                data.pop("_id")
                self._collection.update_one(
                    {"_id": id},
                    {
                        "$set": data,
                    },
                )

            # return True if operation is done
            return True

        except Exception as error:
            # return False if operation is not done
            print(error)
            return False

    def get_all_items_data(self) -> list[dict] | None:
        """
        return items list with all data from collection[items]
        """
        try:
            return list(self._collection.find())

        except Exception as error:
            print(error)

    def get_all_items_obj(self) -> list[dict] | None:
        """
        return items list with all data from collection[items]
        """
        try:
            return [Item(**item) for item in self._collection.find()]

        except Exception as error:
            print(error)

    def get_item_by_id(self, id: str) -> dict | None:
        """
        return item by id
        """
        try:
            return self._collection.find_one({"_id": id})

        except Exception as error:
            print(error)

    def get_item_obj_by_id(self, id: str) -> Item | None:
        """
        return item object by id
        """
        try:
            return Item(**self._collection.find_one({"_id": id}))

        except Exception as error:
            print(error)

    def get_items_obj_by_category_model_subcategory(
        self, category: str, model: str, subcategory: str
    ) -> list[Item] | None:
        """
        return items list by category, model, subcategory
        """
        try:
            return [
                Item(**item)
                for item in self._collection.find(
                    {"category": category, "model": model, "subcategory": subcategory}
                )
            ]

        except Exception as error:
            print(error)

    def delete_item(self, id: str) -> bool:
        """
        delete item by id
        """
        try:
            self._collection.delete_one({"_id": id})
            return True

        except Exception as error:
            print(error)
            return False
