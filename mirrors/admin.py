from django.contrib import admin
from mirrors.models import *


class ComponentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Component, ComponentAdmin)


class ComponentRevisionAdmin(admin.ModelAdmin):
    pass

admin.site.register(ComponentRevision, ComponentAdmin)
