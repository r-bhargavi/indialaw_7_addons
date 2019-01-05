# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, timedelta
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _


class bulk_account_followup(osv.osv_memory):
    
    _name = 'bulk.account.followup'
    _description = 'Bulk Account Followup'
    
    
    _columns = {
        'date': fields.date('Date'),
        'name': fields.text('Description'),
        'next_date': fields.date('Next Date'),
        'state': fields.selection([('communicate', 'To Communicate'),('communicated', 'Communicated'),('completed', 'Completed')], 'Status'),
        'communicate_via': fields.selection([('email', 'Email'),('phone', 'Phone'),('meeting', 'Meeting')], 'Communicated Via'),
        }
        
    
    def create_bulk_account_followup(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        bill_follow_pool = self.pool.get('consolidated.bill.followup')
        invoice_follow_pool = self.pool.get('account.invoice.followup')
        bill_pool = self.pool.get('consolidated.bill')
        invoice_pool = self.pool.get('account.invoice')
        active_ids = context.get('active_ids', False)
        for data in self.browse(cr, uid, ids, context=context):
            current_date = time.strftime('%Y-%m-%d')
            if data.date > current_date:
                raise osv.except_osv(_('Error'),_('Future date selection restricted.'))
            today = datetime.today()
            selected_date = datetime.strptime(data.date, '%Y-%m-%d')
            if selected_date.strftime("%U") != today.strftime("%U"):
                raise osv.except_osv(_('Error'),_("The 'Date' must be in the current week."))
            vals = {
                'date': data.date,
                'name': data.name,
                'next_date': data.next_date,
                'state': data.state,
                'communicate_via': data.communicate_via,
                }
            print 'eeeeeeeeeeeeeeeee',context
            if context.get('active_model', False) == 'account.invoice':
                for invoice_obj in invoice_pool.browse(cr, uid, active_ids, context=context):
                    vals.update({'invoice_id': invoice_obj.id})
                    invoice_follow_pool.create(cr, uid, vals, context=context)
                print 'Single invoices'
            else:
                for bill_obj in bill_pool.browse(cr, uid, active_ids, context=context):
                    vals.update({'bill_id': bill_obj.id})
                    bill_follow_pool.create(cr, uid, vals, context=context)
                print 'Consolidated Invoices'
                    
        return True
        
bulk_account_followup()
