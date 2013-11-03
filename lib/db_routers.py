from local_settings import APP_ROUTERS

class AppRouter(object):

    def db_for_read(self, model, **hints):
        "Point all operations on forum models to particular database"
        return APP_ROUTERS.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        "Point all operations on forum models to particular database"
        return APP_ROUTERS.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in particular database is involved"
        if obj1._meta.app_label in APP_ROUTERS or obj2._meta.app_label in APP_ROUTERS:
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the app only appears on the db where it belongs"
        if db in APP_ROUTERS.values() and model._meta.app_label in APP_ROUTERS:
            return APP_ROUTERS[model._meta.app_label] == db
        elif model._meta.app_label in APP_ROUTERS:
            return False
        return None

