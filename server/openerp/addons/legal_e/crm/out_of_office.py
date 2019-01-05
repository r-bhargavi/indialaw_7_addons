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
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _


class out_of_office(osv.osv):
    _name = 'out.of.office'    
        
    def _get_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            start_dt = datetime.strptime(line.start_date, '%Y-%m-%d')        
            end_dt = datetime.strptime(line.end_date, '%Y-%m-%d')
            duration = ((end_dt - start_dt).days + 1)
            res[line.id] = duration
        return res
        
    _columns = {
        'name':fields.char('Subject'),
        'user_id':fields.many2one('res.users','Person'),
        'reason':fields.text('Reason'),
        'type':fields.selection([('days','Days'),('hours','Hours')],'Out for'),
        'event_type':fields.selection([('birthdays','Birthdays'),('outofoffice','Out of Office')],'Event Type'),
        'start_date':fields.date('From Date'),
        'end_date':fields.date('To Date'),
        'start_time':fields.float('From Time'),
        'end_time':fields.float('To Time'),
        'count':fields.function(_get_count, string='Total Number',type='float'),
    }
    _defaults = {
        'user_id': lambda self, cr, uid, context=None: uid,
        'event_type': lambda *a : 'outofoffice',
    }
    
    def create(self, cr, uid, vals, context=None):
        retvals = super(out_of_office, self).create(cr, uid, vals, context=context)
        
        if retvals:
            line = self.browse(cr, uid, retvals)
            self.validate_dates(cr, uid, [line.id], line.start_date, line.end_date, line.event_type, line.type, context=context)
            self.validate_times(cr, uid, [line.id], line.start_time, line.end_time, line.event_type, line.type, context=context)
        
        return retvals        
    
    def write(self, cr, uid, ids, vals, context=None):
        retvals = super(out_of_office, self).write(cr, uid, ids, vals, context=context)
        for line in self.browse(cr, uid, ids):
            self.validate_dates(cr, uid, [line.id], line.start_date, line.end_date, line.event_type, line.type, context=context) 
            self.validate_times(cr, uid, [line.id], line.start_time, line.end_time, line.event_type, line.type, context=context)
        return retvals    
        
    def validate_dates(self, cr, uid, ids, start_date, end_date, event_type, ttype, context=None):
        if event_type != 'outofoffice' or ttype != 'days':
            return {'value':{}}
        from_date = False
        to_date = False
        if start_date:
            from_date = datetime.strptime(start_date.split(' ')[0], '%Y-%m-%d')
        if end_date:
            to_date = datetime.strptime(end_date.split(' ')[0], '%Y-%m-%d')
            
        if from_date:
            if to_date and (to_date - from_date).days < 0:
                raise osv.except_osv(_('Warning'),_('From Date Should be Less than/ Equal to To Date'))
                return {'value': {'start_date':False}}
        if to_date:
            if from_date and (to_date - from_date).days < 0:
                raise osv.except_osv(_('Warning'),_('To Date Should be Greater than/ Equal to From Date'))
                return {'value': {'end_date':False}}
        return {'value': {}}
        
        
    def validate_times(self, cr, uid, ids, start_time, end_time, event_type, ttype, context=None):
        if event_type != 'outofoffice' or ttype != 'hours':
            return {'value':{}}
        if start_time and end_time:
            if (end_time - start_time) < 0:
                raise osv.except_osv(_('Warning'),_('From Time Should be Less than/ Equal to To Time'))
                return {'value': {'start_date':False}}
        
        return {'value': {}}
        

out_of_office()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: