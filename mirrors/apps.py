import inspect
import importlib

from django import apps

from mirrors import components


class MirrorsConfig(apps.AppConfig):
    name = 'mirrors'
    verbose_name = 'Mirrors'

    def ready(self):
        """
        TODO
        This is where we will load all of the components into
        ComponentSchemaCache and adding them to be validated.
        """
        for app in apps.apps.get_app_configs():
            try:
                comps = importlib.import_module(
                    '%s.components' % app.module.__name__)
            except ImportError:
                pass
            else:
                add_components(comps)


def add_components(comps):
    for component_name in dir(comps):
        component = getattr(comps, component_name)
        if inspect.isclass(component) and \
                issubclass(component, components.Component):
            if component.id not in components.ComponentSchemaCache:
                components.ComponentSchemaCache[component.id] = component
                """
                TODO: Add these to the validator here.
                """
