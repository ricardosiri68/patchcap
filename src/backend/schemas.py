"""
colander schemas for validation
"""
import colander
from models import Device, User
from colanderalchemy import SQLAlchemySchemaNode

class LoginSchema(colander.MappingSchema):
    login_id = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())

DeviceSchema = SQLAlchemySchemaNode(Device,
                              excludes=['updated_on','created_on'],
                              title='Devices')

pwd = colander.SchemaNode(colander.String(), name='password')
UserSchema = SQLAlchemySchemaNode(User,
                              includes= ['id', 'name', 'username', 'email',pwd],
                              excludes=['updated_on','created_on'],
                              title='Users')
 
class RegisterSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), 
                                validator=colander.Email())

class ActivateSchema(RegisterSchema):
    command_id = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())


ForgotSchema = RegisterSchema
ResetSchema = ActivateSchema
