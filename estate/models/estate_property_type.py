from odoo import models, fields
class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "estate.property.type"
    
    name=fields.Char(required=True)
    _sql_constraints=[
    ('estate_property_type_name_uniq', 'unique(name)','A property type name must be unique'),
    ]
    active=fields.Boolean(default=True)