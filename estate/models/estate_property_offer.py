from odoo.exceptions import UserError
from odoo import models, fields,api,_
from dateutil.relativedelta import relativedelta
class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "estate.property.offer"
    price=fields.Float()   
    status=fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')],copy=False)   
    partner_id =fields.Many2one('res.partner',required=True)
    property_id=fields.Many2one('estate.property',required=True)
    active=fields.Boolean(default=True)
    validity=fields.Integer(default=7)
    date_deadline=fields.Date(string='Deadline',compute='_compute_deadline',inverse='_inverse_deadline')
    # state = fields.Selection([
    #     ('accepted', 'Accepted'), ('refused', 'Refused')
    #    ],
    #    copy=False)
    _sql_constraints = [
          ('estate_property_offer_check_price', 'CHECK(price > 0)',
         'An offer price must be strictly positive')
    ]

    @api.depends("create_date","validity")
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline =  record.create_date+relativedelta(days=record.validity)
            else:
                record.date_deadline = False
    def _inverse_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                record.validity = relativedelta(record.date_deadline,record.create_date).days
    def action_accept(self):
        if len(self.property_id.offer_ids.filtered(lambda x:x.status=='accepted'))>0:
            raise UserError(_('Only one offer can be accepted for a given property!' ))
        for record in self:
            record.status='accepted'
            record.property_id.buyer=record.partner_id
            record.property_id.selling_price=record.price            
        return True
    def action_refuse(self):
        for record in self:
            record.status='refused'
            
        return True                