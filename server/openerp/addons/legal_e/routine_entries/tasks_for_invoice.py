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


from openerp.osv import fields, osv
from openerp.tools.translate import _

class tasks_for_invoice(osv.osv):
    _name = 'tasks.for.invoice'    
        
    def _get_invoiced_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}        
        for line in self.browse(cr, uid, ids, context=context):
            total = 0.0
            if line.invoice_id:
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                total = inv.amount_total
            res[line.id] = total    
        return res
        
    def _get_invoiced_balance(self, cr, uid, ids, field_name, arg, context=None):
        res = {}          
        for line in self.browse(cr, uid, ids, context=context):
            residual = 0.0
            if line.invoice_id:
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                residual = inv.residual 
            res[line.id] = residual
        return res
        
    def _get_invoiced_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            state = False
            if line.invoice_id:
                states = {'draft':'Draft','proforma':'Pro-forma','proforma2':'Pro-forma','open':'Open','paid':'Paid','cancel':'Cancelled'}
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                state = states[inv.state]
            res[line.id] = state
        return res
        
    def view_invoice_task(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
        except ValueError, e:
            view_id = False
        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.invoice_id.id,
        }
        
    def view_case_sheet(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'case_sheet_form')
        except ValueError, e:
            view_id = False
        return {
            'name': _('Case Sheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.case_id.id,
        }
        
    
    
    _columns = {
        'case_id': fields.many2one('case.sheet', 'Case Sheet No.', readonly=True),
        'name':fields.many2one('case.tasks.line','Task Related', required=True, readonly=True),
        'assignee_id': fields.many2one('hr.employee', 'Assignee', readonly=True),
        'amount': fields.float('Amount', readonly=True),
        'state': fields.selection([('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Completed','Completed'),('Invoiced','Invoiced')],'Status', readonly=True),
        'invoiced':fields.boolean('Invoiced'),
        'invoice_id':fields.many2one('account.invoice','Invoice ID'),
        'fixed_price_task_id':fields.many2one('fixed.price.stages', 'Fixed Price Task ID'),
        'tm_task_id':fields.many2one('tm.line', 'T & M Task ID'),
        'inv_state': fields.function(_get_invoiced_state,string='INV Status', type='char', readonly=True),
        'inv_total_amt':fields.function(_get_invoiced_total,string='Total INV Amt',type='float',readonly=True),
        'inv_balance_amt':fields.function(_get_invoiced_balance,string='Balance INV Amt',type='float',readonly=True),
        }
    _defaults = {
    	'state':'New',    	
    }
    
    def check_task_in_assignee_tasks(self, cr, uid, ids, taskid, context=None):
        assignids = []
        for line in context['assignee_task_lines']:
            assignids.append(line[2]['name'])
    
        if taskid not in assignids:
            warning = {
                       'title': _('Error!'),
                       'message' : _('Selected Task is not Present in Assignee Tasks.')
                    }
            return {'value': {'name':False}, 'warning': warning}  
        return {'value': {'name':taskid}}  
    
    def invoice_stage(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            partner_id = line.case_id.client_id.id
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            acc_id = p.property_account_receivable.id
            context.update({'type':'out_invoice'})
            product_id=False
            name=line.name.name
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id
                name= line.name.name.name
            inv_id = self.pool.get('account.invoice').create(cr, uid, {'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name':name, 'quantity':1.0,'price_unit':line.amount,'type':'out_invoice'})]},context)
            self.write(cr, uid, [line.id], {'invoiced':True,'invoice_id':inv_id})
            if line.fixed_price_task_id:
                self.pool.get('fixed.price.stages').write(cr, uid, [line.fixed_price_task_id.id], {'invoiced':True,'invoice_id':inv_id})
            if line.tm_task_id:
                self.pool.get('tm.line').write(cr, uid, [line.tm_task_id.id], {'invoiced':True,'invoice_id':inv_id})
        return True
        
        
    def onchange_percent(self, cr, uid, ids, percent, fixed_price, context=None):
        
        if fixed_price:
            amount = (fixed_price*percent)/100
            return {'value':{'amount':amount}}
        else:
            raise osv.except_osv(_('Error!'),_('Enter the Fixed Price Amount First!'))
        return {'value':{'amount':0,'percent_amount':0}}
        
    def onchange_amount(self, cr, uid, ids, amount,fixed_price, context=None):
        if fixed_price:
            percent_amount = (100*amount)/fixed_price
            return {'value':{'percent_amount':percent_amount}}
        else:
            raise osv.except_osv(_('Error!'),_('Enter the Fixed Price Amount First!'))
        return {'value':{'percent_amount':0,'amount':0}}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: