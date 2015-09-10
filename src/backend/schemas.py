"""
colander schemas for validation
"""
import colander


class LoginSchema(colander.MappingSchema):
    login_id = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())

class DeviceSchema(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    ip = colander.SchemaNode(colander.String())
    instream = colander.SchemaNode(colander.String())
    outstream = colander.SchemaNode(colander.String())
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())
    roi = colander.SchemaNode(colander.String())


class RegisterSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), 
                                validator=colander.Email())

class ActivateSchema(RegisterSchema):
    command_id = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())


ForgotSchema = RegisterSchema
ResetSchema = ActivateSchema
