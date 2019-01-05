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

try:
    import simplejson as json
except ImportError:
    import json
import urllib

from openerp.osv import fields, osv
from openerp.tools import ustr


def geo_find(addr):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
    url += urllib.quote(addr.encode('utf8'))

    try:
        result = json.load(urllib.urlopen(url))
    except Exception, e:
        raise osv.except_osv(_('Network error'),
                             _('Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng']), url
    except (KeyError, ValueError):
        return None

def geo_query_address(street=None, tzip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',',1))
    return ustr(', '.join(filter(None, [street,
                                              ("%s %s" % (tzip or '', city or '')).strip(),
                                              state,
                                              country])))


class court_master(osv.osv):
    
    _name = 'court.master'
    
    def _check_name(self, cr, uid, ids, context=None):
        if context is None:
            context = {}           
        name = self.browse(cr, uid, ids[0]).name
        searids = self.search(cr, uid, [('name','=',name),('id','!=',ids[0])]) 
        if len(searids)>0:
                return False
        return True
        
    
    def onchange_number(self, cr, uid, ids, name,number, context=None):
        if not name:
            return {'value': {'ref': False}}
        val = {
            'ref': (name and len(name)>=3 and name[:3].upper()+(number or '') or False)
        }
        return {'value': val}
                
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}
                
    def onchange_district(self, cr, uid, ids, district_id, context=None):
        if district_id:
            state_id = self.pool.get('district.district').browse(cr, uid, district_id, context).state_id.id
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id,'state_id':state_id}}
        return {}
        
    _columns = {
    		'name': fields.char('Court Name',size=128, required=True),
    		'location': fields.char('Court Location',size=128),
    		'number':fields.char('Court No',size=64),
    		'ref':fields.char('Court Id',size=20),
    		'street': fields.char('Street', size=128),
		    'street2': fields.char('Street2'),
    		'zip': fields.char('Zip', change_default=True, size=24),
    		'city': fields.char('City', size=128),
            'landmark':fields.char('LandMark',size=128),
    		'district_id':fields.many2one("district.district",'District'),
    		'state_id': fields.many2one("res.country.state", 'State'),
    		'country_id': fields.many2one('res.country', 'Country'),
            'active': fields.boolean('Active'),
            }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id,line.name+(line.city and ', '+line.city or '')+(line.district_id and ', '+line.district_id.name or '')+(line.state_id and ', '+line.state_id.name or '')))
        return res
        
    
    def geo_localize(self, cr, uid, ids, context=None):
        # Don't pass context to browse()! We need country names in english below
        for partner in self.browse(cr, uid, ids):
            if not partner:
                continue
            url="http://maps.google.com/maps?oi=map&q="
        if partner.street:
            url+=partner.street.replace(' ','+')
        if partner.city:
            url+='+'+partner.city.replace(' ','+')
            if partner.state_id:
                url+='+'+partner.state_id.name.replace(' ','+')
        if partner.country_id:
            url+='+'+partner.country_id.name.replace(' ','+')
        if partner.zip:
            url+='+'+partner.zip.replace(' ','+')
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
        return True
    
    
        
    _constraints = [
        (_check_name, 'Court Name must be Unique!', []),
    ]
    
court_master()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: