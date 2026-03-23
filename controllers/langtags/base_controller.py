from repositories.langtags.base_repository import BaseRepository
from models.langtags.control_fields import ControlFields

class BaseController:
    def __init__(
        self, repository:BaseRepository, model:ControlFields, attributes={ "id": "id", "value": "value" }
    ):
        self.repository = repository
        self.model = model

        self._ATTRIBUTES = attributes

    # Funciones genericas
    def get_columns(self):
        return self.repository.table.get_columns()

    def get_rows(self):
        return self.repository.table.get_rows()

    # Optención de datos para modelo
    def get_row(self, value_id) -> bool:
        row = self.repository.get_row( value_id )
        if len(row) > 0:
            setattr(self.model, self._ATTRIBUTES['id'], row[0])
            setattr(self.model, self._ATTRIBUTES['value'], row[1])
            self.model.created_at = row[2]
            self.model.updated_at = row[3]
            self.model.deleted_at = row[4]
            return True
        else:
            return False

    def get_model_attribute(self, key):
        return getattr(self.model, self._ATTRIBUTES[key])

    def get_value_row(self, value:str) -> bool:
        value_id = self.repository.get_value_id( value )
        return self.get_row( value_id )

    # Modificación de datos
    def activate_model(self):
        return self.repository.activate(
            getattr(self.model, self._ATTRIBUTES['id'])
        )

    def deactivate_model(self):
        return self.repository.deactivate(
            getattr(self.model, self._ATTRIBUTES['id'])
        )

    def save(self, value_id, value, is_deleted):
        save = self.repository.save( value_id, value, is_deleted )
        if self.repository.exists( value_id ):
            self.get_row( value_id )
        else:
            self.get_value_row( value )
        return save

    def is_deleted(self, value_id):
        return self.repository.is_deleted( value_id )

    def is_model_deleted(self):
        return self.is_deleted( getattr(self.model, self._ATTRIBUTES['id']) )

    def exists(self, value_id):
        return self.repository.exists( value_id )
