from django.apps import AppConfig
# django.apps is a module that provides a way to configure and manage Django applications.
# AppConfig is a class within this module that is used to define the configuration for a specific Django application.

class ApiConfig(AppConfig): #Our class ApiConfig inherits from AppConfig, which means it takes on all the properties and methods of AppConfig, but we can also add our own customizations.
    """
    Django expects these 2 variables to be named exactly like this.so it can find them and use them properly.
    this app named api points to the folder named api. everything under backend/api is part of this app.Django uses the app registry (populated via AppConfig)
    to find our models, run migrations, and wire admin, signals, etc.
    """
    default_auto_field = "django.db.models.BigAutoField" # tells django what type of id field to create by default for models that don't explicitly define a primary key.
    # BigAutoField is a 64-bit integer that auto-increments.  So now using Models.model in our models file will create an id field that can handle a huge number of records without running out of IDs.
    name = "api"

