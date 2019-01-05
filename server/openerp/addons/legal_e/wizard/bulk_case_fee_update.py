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

import re
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp import netsvc


class bulk_case_fee_update(osv.osv_memory):
    
    _name = 'bulk.case.fee.update'
    _description = 'Bulk Case Fee Update'
       
    _columns = {
        'flg_first_row':fields.boolean('The first row of the file contains the label of the column'),
        'field_delimiter':fields.selection([(',',','),(';',';'),(':',':')], 'Field Delimiter'),
        'text_delimiter':fields.selection([('"','"'),("'","'")], 'Text Delimiter'),
        'datas': fields.binary('File Content'),
        }
        
    _defaults = {
        'field_delimiter':',',
        'text_delimiter':'"',
        'flg_first_row': True
        }
        
    def generate_bulk_case_fee_update(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        case_pool = self.pool.get('case.sheet')
        office_pool = self.pool.get('ho.branch')
        fixed_pool = self.pool.get('fixed.price.stages')
        case_tasks_pool = self.pool.get('case.tasks.line')
        task_pool = self.pool.get('task.master')
        
        wf_service = netsvc.LocalService("workflow")
        ir_pool = view_ref = self.pool.get('ir.model.data')
        summary = ''
        for line in self.browse(cr, uid, ids, context=context):
            csvfile = line.datas.decode('base64')
            rowcount = 0
            csvsplit = csvfile.split('\n')
            for row in range(rowcount,len(csvsplit)):
                csvsplit[row]=re.sub(r'[^\x00-\x7f]',r'',csvsplit[row])
                cells = csvsplit[row].split(line.field_delimiter)
                text_delimiter = ''
                if line.text_delimiter:
                    text_delimiter = line.text_delimiter
                if len(cells)>1:
                    cells[0] = cells[0].replace(text_delimiter,"")
                    cells[1] = cells[1].replace(text_delimiter,"")
                    cells[2] = cells[2].replace(text_delimiter,"")
                    cells[3] = cells[3].replace(text_delimiter,"")
                    cells[4] = cells[4].replace(text_delimiter,"")
                    case_ids = []
                    if cells[0] and cells[2] and cells[3]:
                        fixed_ids = []
                        case_ids = case_pool.search(cr, uid, [('name', '=', cells[0])], context=context)
                        office_ids = office_pool.search(cr, uid, [('name', '=', cells[3])], context=context)
                        tasks_ids = task_pool.search(cr, uid, [('name', '=', cells[2])], context=context)
                        if tasks_ids and office_ids:
                            case_tasks_ids = case_tasks_pool.search(cr, uid, [('name', 'in', tasks_ids)], context=context)
                            if case_tasks_ids:
                                fixed_ids = fixed_pool.search(cr, uid, [('name', 'in', case_tasks_ids),('office_id', '=', office_ids[0]), ('case_id', 'in', case_ids)], context=context)


                        if case_ids and fixed_ids:
                            fixed_pool.write(cr, uid, fixed_ids, {'amount': cells[4]},context=context)
                            case_pool.write(cr, uid, case_ids, {'fixed_price': cells[1]},context=context)

                            
                            
                    elif cells[2] and cells[3] and case_ids:
                        fixed_ids = []
                        office_ids = office_pool.search(cr, uid, [('name', '=', cells[3])], context=context)
                        tasks_ids = task_pool.search(cr, uid, [('name', '=', cells[2])], context=context)
                        if tasks_ids and office_ids:
                            case_tasks_ids = case_tasks_pool.search(cr, uid, [('name', 'in', tasks_ids)], context=context)
                            if case_tasks_ids:
                                fixed_ids = fixed_pool.search(cr, uid, [('name', 'in', case_tasks_ids),('office_id', '=', office_ids[0]), ('case_id', 'in', case_ids)], context=context)
                        if fixed_ids:
                            fixed_pool.write(cr, uid, fixed_ids, {'amount': cells[4]},context=context)
                
        view_id = False
        
        view_ref = ir_pool.get_object_reference(cr, uid, 'legal_e', 'bulk_case_fee_update_closed')
        view_id = view_ref and view_ref[1] or False,
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Case Fee Update'),
            'res_model': 'bulk.case.fee.update',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            }
        
bulk_case_fee_update()
