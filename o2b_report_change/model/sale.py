# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime
from datetime import timedelta 

class SaleOrder(models.Model):
    _inherit = "sale.order"

    po_number = fields.Char(string="PO Number")
    so_project = fields.Char(string="Project Name")
    lead_days = fields.Char(string="Lead Days")
    expected_delivery_date = fields.Date(string="Expected Delivey Date",readonly=True)
    note_lines = fields.Char(string="Note Lines")

    @api.onchange('lead_days')
    def _set_expected_date(self):
        current_datetime = datetime.datetime.now()
        days = 0
        if self.lead_days:
            days = int(self.lead_days)
        expected_del_date = current_datetime + timedelta(days=days)
        self.expected_delivery_date = expected_del_date.strftime("%Y-%m-%d")

    # add readonly field during onchange
    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['expected_delivery_date']
        if values.get('lead_days') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line._set_expected_date()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model
    def create(self, vals):
        vals.update(self._prepare_add_missing_fields(vals))
        return super(SaleOrder,self).create(vals)
              
    @api.multi
    def write(self, vals):
        vals.update(self._prepare_add_missing_fields(vals))
        return super(SaleOrder,self).write(vals)
    
    @api.multi
    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        days = 0
        if self.lead_days:
            days = int(self.lead_days)
        confirmation_date = fields.Date.from_string(self.confirmation_date) #convert into date formate
        expected_del_date = confirmation_date +timedelta(days=days)
        expected_date_val = expected_del_date.strftime("%Y-%m-%d")
        self.write({'expected_delivery_date':expected_date_val})
        return res

    # shipment date populate from SO 
    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder,self)._prepare_invoice()
        res.update({'shipment_date':self.expected_delivery_date})
        return res


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    po_number = fields.Char(string="PO Number")
    ship_via = fields.Char(string="Ship Via")
    shipment_date = fields.Date(string="Shipment Date",readonly=True)
    note_lines = fields.Char(string="Note Lines")

    def number_change(self):
        inv = ''
        if self.number:
            number = str(self.number)
            a,b,c = number.split('/')
            b = b[2:]
            inv = str(a)+str(b)+str(c)
        return inv


class partner(models.Model):
    _inherit = "res.partner"

    x_studio_field_AA4JU = fields.Char(String="Fax")