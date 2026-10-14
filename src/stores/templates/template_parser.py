import os
import logging

class TemplateParser:

    def __init__(self, language: str = None, defualt_language: str = "en"):
        
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.language = language
        self.defualt_language = defualt_language
        self.logger = logging.getLogger(__name__)

    def set_language(self, language: str):
        lan_path = os.path.join(self.current_path, "locales", language)
        if language and os.path.exists(lan_path):
            self.language = language
        else:
            self.language = self.defualt_language

    def get(self, group: str, key: str, vars: dict = {}):
        if not group:
            self.logger.error("No group was provided to get")
            return None

        if not key:
            self.logger.error("No key was provided to get")
            return None

        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py")
        
        target_language = self.language
        if not os.path.exists(group_path):
            group_path = os.path.join((self.current_path, "locales", self.defualt_language, f"{group}.py"))
            target_language = self.defualt_language

        if not os.path.exists(group_path):
            self.logger.error("group path was not found")
            return None

        module = __import__(f"stores.templates.locales.{target_language}.{group}", fromlist=[group])
        if not module:
            self.logger.error("The module was not found")
            return None

        key_attr = getattr(module, key)
        if not key_attr:
            self.logger.error("no attribute was found in the module")
            return None

        return key_attr.substitute(vars)