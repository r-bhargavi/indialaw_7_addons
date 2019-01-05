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


import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class case_cancel(osv.osv_memory):

    _name = "case.cancel"
    _description = "Cancel Case Sheet"

    _columns = {
        'name': fields.text('Reason'),
        'cancel_date':fields.date('Cancel Date'),
    }
    _defaults = {
        'cancel_date':lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def cancel_case_sheet(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        case_id = context.get('active_id', False)
        for case_obj in self.pool.get('case.sheet').browse(cr, uid, [case_id], context=context):
            self.pool.get('project.project').set_cancel(cr, uid, [case_obj.project_id.id], context=context)
            type_ids = self.pool.get('project.task.type').search(cr, uid, [('state', '=', 'cancelled')], context=context)
            if type_ids:
                cr.execute("update project_task set state='cancel', stage_id=%s  where project_id=%s;",(type_ids[0], case_obj.project_id.id))
            
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('case_id', '=', case_id)], context=context)
        for inv_obj in self.pool.get('account.invoice').browse(cr, uid, invoice_ids, context=context):
            if inv_obj.state != 'cancel':
                raise osv.except_osv(_('Warning!'),_('Please cancel the invoices related to this case sheet!'))
        return self.pool.get('case.sheet').write(cr, uid, [case_id], {'state':'cancel','cancel_comments':context['comments'],'cancel_date':context['cancel_date']})

case_cancel()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: