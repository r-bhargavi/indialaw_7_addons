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
from datetime import datetime, timedelta

from openerp.osv import fields, osv
import calendar


class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def run_scheduler_birthdays(self, cr, uid, context=None):
        if not context:
            context = {}
        emp_searids = self.search(cr, uid, [])
        today_ids = []
        week_ids = []
        month_ids = []
        false_ids = []
        today = time.strftime('%Y-%m-%d')
        dt = datetime.strptime(today, '%Y-%m-%d')
        week_start = dt - timedelta(days = dt.weekday())
        week_end = week_start + timedelta(days = 6)
        month_start_week_day,month_total_days = calendar.monthrange(int(time.strftime('%Y')),int(time.strftime('%m')))
        month_start = datetime.strptime(time.strftime('%Y')+'-'+time.strftime('%m')+'-01', '%Y-%m-%d')
        month_end = datetime.strptime(time.strftime('%Y')+'-'+time.strftime('%m')+'-'+str(month_total_days) , '%Y-%m-%d')        
        
        for obj in self.pool.get('hr.employee').browse(cr, uid, emp_searids):
            if obj.birthday:
                bitrhday_this_year = time.strftime('%Y')+'-'+datetime.strptime(obj.birthday, '%Y-%m-%d').strftime("%m")+'-'+datetime.strptime(obj.birthday, '%Y-%m-%d').strftime("%d")
                if datetime.strptime(obj.birthday, '%Y-%m-%d').strftime("%d") == time.strftime('%d') and datetime.strptime(obj.birthday, '%Y-%m-%d').strftime("%m") == time.strftime('%m'):
                    today_ids.append(obj.id)
                elif datetime.strptime(bitrhday_this_year, '%Y-%m-%d')>=week_start and datetime.strptime(bitrhday_this_year, '%Y-%m-%d')<=week_end:     
                    week_ids.append(obj.id)
                elif datetime.strptime(bitrhday_this_year, '%Y-%m-%d')>=month_start and datetime.strptime(bitrhday_this_year, '%Y-%m-%d')<=month_end:     
                    month_ids.append(obj.id)
                else:
                    false_ids.append(obj.id)
                #To Set the Birthday String for First Time
                if not obj.birthday_string:
                    self.set_birthday_string(cr, uid,[obj.id], context=context)
                #To Update the Calendar View    
                if len(self.pool.get('ir.model').search(cr, uid, [('model','=','out.of.office')])):    
                        name = obj.name + '\'s Birthday'
                        start_date = bitrhday_this_year
                        end_date = bitrhday_this_year
                        user_id = obj.user_id.id
                        updated_birthday = False
                        type = 'days'
                        event_type = 'birthdays'
                        if context.has_key('emp_id') and context['emp_id'] == obj.id and context.has_key('updated_birthday') and context['updated_birthday']:
                            updated_birthday = time.strftime('%Y')+'-'+datetime.strptime(context['updated_birthday'], '%Y-%m-%d').strftime("%m")+'-'+datetime.strptime(context['updated_birthday'], '%Y-%m-%d').strftime("%d")   
                            start_date = updated_birthday
                            end_date = updated_birthday
                            
                        if not len(self.pool.get('out.of.office').search(cr, uid, [('name','=',name), ('user_id','=',user_id), ('type','=',type), ('event_type','=',event_type)])):
                            self.pool.get('out.of.office').create(cr, uid, {'name':name, 'user_id':user_id, 'type':type, 'event_type':event_type, 'start_date':start_date, 'end_date':end_date})
                        elif updated_birthday and len(self.pool.get('out.of.office').search(cr, uid, [('name','=',name), ('user_id','=',user_id), ('type','=',type), ('event_type','=',event_type)])):
                            searids = self.pool.get('out.of.office').search(cr, uid, [('name','=',name), ('user_id','=',user_id), ('type','=',type), ('event_type','=',event_type)])
                            for l in self.pool.get('out.of.office').browse(cr, uid, searids):
                                l.write({'start_date':updated_birthday,'end_date':updated_birthday})
                        elif updated_birthday and not len(self.pool.get('out.of.office').search(cr, uid, [('name','=',name), ('user_id','=',user_id), ('type','=',type), ('event_type','=',event_type)])):
                            self.pool.get('out.of.office').create(cr, uid, {'name':name, 'user_id':user_id, 'type':type, 'event_type':event_type, 'start_date':start_date, 'end_date':end_date})
                        elif not len(self.pool.get('out.of.office').search(cr, uid, [('name','=',name), ('user_id','=',user_id), ('type','=',type), ('event_type','=',event_type),('start_date','=',start_date), ('end_date','=',end_date)])):
                            self.pool.get('out.of.office').create(cr, uid, {'name':name, 'user_id':user_id, 'type':type, 'event_type':event_type, 'start_date':start_date, 'end_date':end_date})    
                            
            else:
                false_ids.append(obj.id)                    
        self.write(cr, uid, today_ids,{'birthday_select':'1'})
        self.write(cr, uid, week_ids,{'birthday_select':'2'})
        self.write(cr, uid, month_ids,{'birthday_select':'3'})
        self.write(cr, uid, false_ids,{'birthday_select':False})
        
        return True
        
    def set_birthday_string(self, cr, uid, ids, context=None):        
        #emp_searids = self.search(cr, uid, [])
        for obj in self.browse(cr, uid, ids):
            if obj.birthday and not obj.birthday_string:
                dt = datetime.strptime(obj.birthday, '%Y-%m-%d')
                bstring = dt.strftime("%d")+' '+dt.strftime("%B")
            else:
                bstring = False
            self.write(cr, uid, [obj.id], {'birthday_string':bstring})    
        return True
        
    def onchange_birthday(self, cr, uid, ids, birthday, context=None):
        if not context:
            context = {}
        res = {}
        if birthday:
            bdt = datetime.strptime(birthday, '%Y-%m-%d')
            res['birthday_string'] = bdt.strftime("%d")+' '+bdt.strftime("%B")
            today = time.strftime('%Y-%m-%d')
            dt = datetime.strptime(today, '%Y-%m-%d')
            week_start = dt - timedelta(days = dt.weekday())
            week_end = week_start + timedelta(days = 6)
            month_start_week_day,month_total_days = calendar.monthrange(int(time.strftime('%Y')),int(time.strftime('%m')))
            month_start = datetime.strptime(time.strftime('%Y')+'-'+time.strftime('%m')+'-01', '%Y-%m-%d')
            month_end = datetime.strptime(time.strftime('%Y')+'-'+time.strftime('%m')+'-'+str(month_total_days) , '%Y-%m-%d')
            bitrhday_this_year = time.strftime('%Y')+'-'+datetime.strptime(birthday, '%Y-%m-%d').strftime("%m")+'-'+datetime.strptime(birthday, '%Y-%m-%d').strftime("%d")
            if datetime.strptime(birthday, '%Y-%m-%d').strftime("%d") == time.strftime('%d') and datetime.strptime(birthday, '%Y-%m-%d').strftime("%m") == time.strftime('%m'):
                res['birthday_select'] = '1'
            elif datetime.strptime(bitrhday_this_year, '%Y-%m-%d')>=week_start and datetime.strptime(bitrhday_this_year, '%Y-%m-%d')<=week_end:     
                res['birthday_select'] = '2'
            elif datetime.strptime(bitrhday_this_year, '%Y-%m-%d')>=month_start and datetime.strptime(bitrhday_this_year, '%Y-%m-%d')<=month_end:    
                res['birthday_select'] = '3'
            else:
                res['birthday_select'] = False 
        
        else:
            res['birthday_select'] = False
            res['birthday_string'] = False
        context['emp_id'] = len(ids) and ids[0] or False
        context['updated_birthday'] = birthday
        self.run_scheduler_birthdays(cr, uid, context=context)    
        return {'value':res}      
    
    _columns={
    	'birthday_select':fields.selection([('1','Today'),('2','This Week'),('3','This Month')],'Birthday Selection'),
    	'birthday_string':fields.char('Birthday'),    
        }
    
    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        retvals = super(hr_employee, self).create(cr, uid, vals, context=context)    
        self.run_scheduler_birthdays(cr, uid, context=context)
        return retvals    
    
hr_employee()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: