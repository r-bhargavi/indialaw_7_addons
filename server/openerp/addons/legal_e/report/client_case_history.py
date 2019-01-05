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
from datetime import datetime
from openerp.report import report_sxw
from openerp.osv import orm

class client_case_history_all(report_sxw.rml_parse):
    _name = 'report.client.case.history'
    def __init__(self, cr, uid, name, context=None):
        super(client_case_history_all, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'datetime':datetime,
            'get_data':self.get_data,
            'get_current_date':self.get_current_date,
            'get_client_name':self.get_client_name,
            'format_date':self.format_date,
            'check_proceedings':self.check_proceedings,
            'get_data_proceedings':self.get_data_proceedings,
            'get_prepared_by':self.get_prepared_by,
        })        
    
    def filter_proceedings(self, cr, uid, data, context=None):
        filters = []
        
        context = data['form']
        if context.has_key('case_id') and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if context.has_key('client_id') and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id'])) 
        if context.has_key('state') and context['state']!=False:
            filters.append(('state','=',context['state']))
        if context.has_key('ho_branch_id') and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
            
        return filters
        
    def get_data(self, data):
        try:
            ret_datas = []
            ret_data = {}
            if data.has_key('form') and data['form'].has_key('case_lines') and len(data['form']['case_lines']):
                for case in self.pool.get('case.sheet').browse(self.cr, self.uid, data['form']['case_lines']):
                    first_parties = ''
                    opp_parties = ''
                    parties = ''
                    court = ''
                    procount = 0    
                    state_list = {'new':'New','inprogress':'In Progress','cancel':'Cancelled','transfer':'Transferred', 'won':'Won', 'arbitrated':'Arbitrated', 'withdrawn':'With Drawn', 'lost':'Lost', 'inactive':'Inactive', 'done':'Closed', 'hold': 'Hold'}
                    work_types = {'civillitigation':'Civil Litigation','criminallitigation':'Criminal Litigation', 'non_litigation':'Non Litigation', 'arbitration':'Arbitration', 'execution':'Execution', 'mediation':'Mediation'}
                    
                    for first in case.first_parties:
                        first_parties += (first_parties!='' and ', ' + first.name or first.name)
                    parties = first_parties + '<b>v/s</b>'
                    first_parties += ' v/s ' 
                    for opp in case.opp_parties:
                        opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                    parties += opp_parties
                    
                    if case.work_type in ('civillitigation','criminallitigation', 'execution'):
                        court = (case.court_id and case.court_id.name or '') + (case.court_location_id and ', ' + case.court_location_id.name or '') + (case.court_district_id and ', ' + case.court_district_id.name or '')
                    else:
                        court = work_types[case.work_type] + ', ' + case.casetype_id.name
                    pro_search_ids = self.pool.get('court.proceedings').search(self.cr, self.uid, [('case_id','=',case.id)])
                    for proceed in case.court_proceedings:
                        ret_data = {}
                        if procount ==0:
                            ret_data['name'] = case.name
                            ret_data['first_parties'] = first_parties
                            ret_data['opp_parties'] = opp_parties
                            ret_data['court'] = court
                            ret_data['status'] = state_list[case.state]
                        else:                            
                            ret_data['name'] = ''
                            ret_data['first_parties'] = ''
                            ret_data['opp_parties'] = ''
                            ret_data['court'] = ''
                            ret_data['status'] = ''
                        ret_data['proceed_date'] = (proceed.proceed_date and datetime.strptime(proceed.proceed_date, '%Y-%m-%d').strftime('%d/%m/%Y') or '')
                        ret_data['proceed_name'] = proceed.name
                        ret_data['next_proceed_date'] = (proceed.next_proceed_date and datetime.strptime(proceed.next_proceed_date, '%Y-%m-%d').strftime('%d/%m/%Y') or '')
                        procount += 1
                        if len(pro_search_ids) == procount:
                            ret_data['last_line'] = True
                        else:
                            ret_data['last_line'] = False
                        ret_datas.append(ret_data)

                    if procount ==0:
                        ret_data = {}
                        ret_data['name'] = case.name
                        ret_data['first_parties'] = first_parties
                        ret_data['opp_parties'] = opp_parties
                        ret_data['court'] = court
                        ret_data['status'] = state_list[case.state]
                        ret_data['proceed_date'] = ''
                        ret_data['proceed_name'] = ''
                        ret_data['next_proceed_date'] = ''
                        ret_data['last_line'] = True
                        ret_datas.append(ret_data)    
                        
                return ret_datas
        except NameError:
                raise orm.except_orm(_(''),
                     _('No Data To Generate Report'))
        
    def get_current_date(self):
        return time.strftime('%d/%m/%Y')
        
    def get_client_name(self, data):
        if data.has_key('form') and data['form'].has_key('client_id') and data['form']['client_id']:
            return self.pool.get('res.partner').read(self.cr, self.uid, data['form']['client_id'],['name'])['name']
        return ''
        
    def format_date(self, date, format):
        return datetime.strptime(date, '%Y-%m-%d').strftime(format)
        
    def check_proceedings(self, case_id):
        search_ids = self.pool.get('court.proceedings').search(self.cr, self.uid, [('case_id','=',case_id)])
        if len(search_ids):
            return True
        return False  
        
    def get_data_proceedings(self, case_id):
        search_ids = self.pool.get('court.proceedings').search(self.cr, self.uid, [('case_id','=',case_id)])
        return self.pool.get('court.proceedings').browse(self.cr, self.uid, search_ids)
        
    def get_prepared_by(self,data):
        return self.pool.get('res.users').read(self.cr, self.uid, self.uid, ['name'])['name']
        return ''
    
report_sxw.report_sxw('report.client.case.history', 'case.sheet', 'addons/legal_e/report/client_case_history_view.rml', parser=client_case_history_all, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: