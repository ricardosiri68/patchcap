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
                              excludes=['updated_on','created_on', 'updated_by', 'logs'],
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
                    overrides={'roi':{'missing': None, 'default': None},
                               'correction':{'missing': None, 'default': None},
                               'conf':{'missing': None, 'default': None},
                               'code':{'missing': None, 'default': None},
                              'ts':{'missing': None, 'default': None}},
                    excludes=['updated_on','created_on', 'updated_by', 'device', 'correction'])

UserSchema = SQLAlchemySchemaNode(User,
        overrides= {'password': {'typ':colander.String, 'default':None},
                    'devices': {'includes':['id'], 'default':[]},
                    'profiles': {'includes':['id','name'], 'default':[]}},
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
