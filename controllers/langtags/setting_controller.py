from repositories.langtags.setting_repository import SettingRepository
from models.langtags.setting import Setting

class SettingController():
    def __init__(
        self, repository: SettingRepository, model: Setting
    ):
        self.repository = repository
        self.model = model

    # Funciones genericas
    def get_columns(self):
        return self.repository.table.get_columns()

    def get_rows(self):
        return self.repository.table.get_rows()

    # Especificas
    def get_language_codes(self):
        return self.repository.get_language_codes()

    def get_language_ids(self):
        return self.repository.get_language_ids()

    def get_language_dict(self):
        dictionary = {}
        codes = self.repository.get_language_codes()
        ids = self.repository.get_language_ids()
        number = 0
        for code in codes:
            dictionary.update( {code: ids[number]} )
            number += 1
        return dictionary

    def get_current_language_model(self):
        self.model.setting_id = self.repository.select_parameter_id( 'current_language' )
        self.model.parameter_name = 'current_language'
        self.model.language_id = self.repository.select_current_language_id()

    def select_current_language_code(self):
        if self.repository.is_current_language_system():
            return 'system_language'
        elif self.repository.is_current_language_default():
            return 'default_language'
        else:
            return self.select_current_language_code()

    def update_current_language_code(self, code):
        update = self.repository.update_current_language_code( code )
        if update:
            self.get_current_language_model()
        return update

    def update_current_language_id(self, language_id):
        update = self.repository.update_current_language_id( language_id )
        if update:
            self.get_current_language_model()
        return update
