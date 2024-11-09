from odoo import models, fields
from dateutil.relativedelta import relativedelta
# from datetime import timedelta
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "estate.property"
    
    name=fields.Char(required=True)
    description=fields.Text()
    postcode=fields.Char()
    date_availability=fields.Date(copy=False,default=fields.date.today() + relativedelta(months=3))
    expected_price=fields.Float(required=True)
    selling_price=fields.Float(readonly=True, copy=False)
    bedrooms=fields.Integer(default=2)
    living_area=fields.Integer()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Integer()
    active=fields.Boolean(default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('received', 'Offer Received'),
        ('accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')],
        default='new', required=True, copy=False)
   
    garden_orientation=fields.Selection(selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    property_type_id=fields.Many2one('estate.property.type','Type')
    buyer =fields.Many2one('res.partner',copy=False)
    salesperson=fields.Many2one('res.partner',default=lambda self:self.env.user.partner_id)
    tag_ids=fields.Many2many('estate.property.tag',string='Tags')
    offer_ids=fields.One2many('estate.property.offer','property_id',string="Offers")