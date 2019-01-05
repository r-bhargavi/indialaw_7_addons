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
from openerp import SUPERUSER_ID


class consolidated_bulk_case_sheet(osv.osv_memory):
    
    _name = 'consolidated.bulk.case.sheet'
    _description = 'Consolidated Bulk Case Sheet'
    _inherit = ['mail.thread']
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:                
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas  
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(consolidated_bulk_case_sheet, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(consolidated_bulk_case_sheet, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
        
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id,line.name.name))
        return res
    
    
    _columns = {
    		'name': fields.many2one('case.sheet','File Number to Duplicate'),
    		'flg_first_row':fields.boolean('The first row of the file contains the label of the column'),
    		'field_delimiter':fields.selection([(',',','),(';',';'),(':',':')],'Field Delimiter'),
    		'text_delimiter':fields.selection([('"','"'),("'","'")],'Text Delimiter'),
    		'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    		'datas_fname': fields.char('File Content',size=256, required=True),
    		'store_fname': fields.char('Stored Filename', size=256),
        	'db_datas': fields.binary('Database Data'),
        	'file_size': fields.integer('File Size'),
        	'attach_id': fields.many2one('ir.attachment','Attachment ID'),
        }
        
    _defaults = {
                'field_delimiter':',',
                'text_delimiter':'"',
    }
    
    def update_consolidated_bill_casesheet(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            case_ids = []
            csvfile = line.datas.decode('base64')
            rowcount = 0
            if line.flg_first_row:
                rowcount = 1
            csvsplit = csvfile.split('\n')    
            for row in range(rowcount,len(csvsplit)):
                cells = csvsplit[row].split(line.field_delimiter)
                if len(cells) and cells[0].replace(line.text_delimiter,"").strip()!='':
                    cells[0] = cells[0].replace(line.text_delimiter,"")
                    refsearchids = self.pool.get('case.sheet').search(cr, uid, [('name','=',cells[0].strip()),('client_id','=',context['client_id']),('work_type','=',context['work_type']),('casetype_id','=',context['casetype_id'])])
                    
                    if not len(refsearchids):
                        raise osv.except_osv(_('Error'),_('File Number "%s" is NOT present in the selected Client Case Details.'%cells[0]))
                    else:
                        case_ids.append(refsearchids[0])
            if len(case_ids):                
                for case_id in case_ids:
                    for act in context['active_ids']:
                        self.pool.get('consolidated.bill').write(cr, uid, [act],{'case_sheet_ids':[(4,case_id)]})            
        return True
        
    def create(self, cr, uid, vals, context=None): 
        if context is None:
            context = {}
        retvals = super(consolidated_bulk_case_sheet, self).create(cr, uid, vals, context=context)
        return retvals
        
consolidated_bulk_case_sheet()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: