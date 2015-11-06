"""
colander schemas for validation
"""
import colander
from models import Device, User, Profile, Log, Plate, Alarm
from colanderalchemy import SQLAlchemySchemaNode

class LoginSchema(colander.MappingSchema):
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())

DeviceSchema = SQLAlchemySchemaNode(Device,
                              excludes=['updated_on','created_on', 'updated_by'],
                              overrides={'roi':{'missing': None, 'default': None},
                                         'ip':{'missing': None, 'default': None}},
                              title='Devices')

ProfileSchema = SQLAlchemySchemaNode(Profile,
                    excludes=['updated_on','created_on', 'updated_by','users'])

AlarmSchema = SQLAlchemySchemaNode(Alarm,
                    excludes=['updated_on','created_on', 'updated_by'])

PlateSchema = SQLAlchemySchemaNode(Plate,
                    excludes=['updated_on','created_on', 'updated_by'])

LogSchema = SQLAlchemySchemaNode(Log,
                    excludes=['updated_on','created_on', 'updated_by'])

UserSchema = SQLAlchemySchemaNode(User,
        overrides= {'password': {'typ':colander.String, 'default':None},
                        'profiles':{'includes':['id','name'],
                                    'default':[]}}, 
                        excludes=['updated_on','created_on', 'updated_by'],
                        title='Users')

 
class RegisterSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), 
                                validator=colander.Email())

class ActivateSchema(RegisterSchema):
    command_id = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())


ForgotSchema = RegisterSchema
ResetSchema = ActivateSchema
