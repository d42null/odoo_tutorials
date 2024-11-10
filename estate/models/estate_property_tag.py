from odoo import models, fields
class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "estate.property.tag"
    
    name=fields.Char(required=True)
    _sql_constraints = [
    ('estate_property_tag_name_uniq', 'unique(name)', "A property tag name must be unique"),
    ]
    active=fields.Boolean(default=True)