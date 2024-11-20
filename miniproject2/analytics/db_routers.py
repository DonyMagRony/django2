class AnalyticsRouter:
    """
    A router to control all database operations on models in the
    analytics application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read analytics models go to the analytics database.
        """
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write analytics models go to the analytics database.
        """
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that the analytics app only migrates to the analytics database.
        """
        if app_label == 'analytics':
            return db == 'analytics'
        return None
