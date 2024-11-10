from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_compare
from odoo import models, fields,api,_
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
        ('canceled', 'Canceled')],
        default='new', required=True, copy=False)
   
    garden_orientation=fields.Selection(selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    property_type_id=fields.Many2one('estate.property.type','Type')
    buyer =fields.Many2one('res.partner',copy=False)
    salesperson=fields.Many2one('res.partner',default=lambda self:self.env.user.partner_id)
    tag_ids=fields.Many2many('estate.property.tag',string='Tags')
    offer_ids=fields.One2many('estate.property.offer','property_id',string="Offers")
    total_area = fields.Integer(compute="_compute_total_area")
    best_price=fields.Float(string='Best Offer', compute='_compute_best_price')
    
    _sql_constraints = [
          ('check_expected_price', 'CHECK(expected_price > 0)',
         'A property expected price must be strictly positive'),
             ('check_selling_price', 'CHECK(selling_price >= 0)',
         'A property selling price must be positive')      
    ]

    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
            
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price=max(record.offer_ids.mapped('price'))
            else:
                record.best_price=False
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation ='north'
        else:
            self.garden_area = False
            self.garden_orientation =False
    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise UserError(_('Canceled properties can not be sold' ))
            else :
                record.state='sold'
        return True
    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError(_('Sold properties can not be canceled' ))
            else :
                record.state='canceled'
        return True
    @api.constrains('expected_price','selling_price')
    def _check_date_end(self):
        for record in self:
            if float_compare(record.selling_price, record.expected_price*0.9,2)==-1:
                raise ValidationError("The selling price cannot be lower than 90% of the expected price")