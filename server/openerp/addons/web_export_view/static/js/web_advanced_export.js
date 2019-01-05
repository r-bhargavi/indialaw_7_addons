//  @@@ web_export_view custom JS @@@
//#############################################################################
//    
//    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
//    Copyright (C) 2012 Therp BV (<http://therp.nl>)
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as published
//    by the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//#############################################################################

openerp.web_export_view = function(instance, m) {

    var _t = instance.web._t,
    QWeb = instance.web.qweb;
    flg=true;
    curr_data={}
    export_columns_keys = [];
    export_columns_names = [];
    export_rows = [];
    check_count=0;
    data_count=0;
    instance.web.Sidebar.include({
        redraw: function() {
            var self = this;
            this._super.apply(this, arguments);
            //self.$el.find('.oe_sidebar').append(QWeb.render('AddExportViewMain', {widget: self}));
            self.$el.find('.oe_bold oe_list_button_import_excel oe_form_button').on('click', self.on_sidebar_export_view_xls);
            var links = document.getElementsByClassName("oe_list_button_import_excel");
            if (links && links[0]){
                links[0].onclick = function() {
                    self.on_sidebar_export_view_xls();
                };
            }
        },
	fetchval: function(id_val){
	 retval = new instance.web.Model("export.carrier.data").call('write', [[parseInt(id_val)], {'exported':true}]);
	 return new instance.web.Model("export.carrier.data").get_func("read")(parseInt(id_val), [])
	},
        on_sidebar_export_view_xls: function() {
            flg=true;
	    curr_data={}
	    export_columns_keys = [];
	    export_columns_names = [];
	    export_rows = [];
	    check_count=0;
	    data_count=0;
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
           
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
           
            start: 
           /* $.each(view.visible_columns, function(){
            
                if(this.tag=='field'){                	
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);                    
                    export_columns_names.push(this.string);
                }
            });*/
            var column_keys = ['ref_no','carrier','service','receiver_code','receiver_name','add1','add2','add3','receiver_suburb','receiver_state','receiver_postcode','receiver_contact','receiver_phone','receiver_email','inst_1','inst_2','inst_3','sender_code','line_ref','qty','item_code','item_desc','line_weight','line_m3'];
            var column_names = ['Reference Number','Carrier','Service','Receiver Code','Receiver Name','Receiver Address 1','Receiver Address 2','Receiver Address 3','Receiver Suburb','Receiver State','Receiver Postcode','Receiver Contact','Receiver Phone','Receiver Email','Special Instructions Line 1','Special Instructions Line 2','Special Instructions Line 3','Sender Code','Goods detail line reference number','Goods detail line number of items','Packing or item code','Packing or item description','Goods detail line total weight in KG','Goods detail line total volume in m3'];
            for(i=0;i<column_keys.length;i++)
            {
            	export_columns_keys.push(column_keys[i]);                    
            	export_columns_names.push(column_names[i]);
            }
            //export_columns_keys.push('categ_id');                    
            //export_columns_names.push('Category ID');
            rows = view.$el.find('.oe_list_content > tbody > tr');
            
            //var Model = new instance.web.Model('res.users');
            check_count = $('input[name="radiogroup"]:checked').length;
            total_rows = $('input[name="radiogroup"]').length;
            if(check_count<=0)
            {
            	alert('Please Select record(s) to Export');
            	return;
            }
            else
            {
            	//for(cnt=0;cnt<total_rows;cnt++)
            	{
            		
            	}
            }
            $('.oe_list_content tr').each(function (i, row) {
	
        // reference all the stuff you need first
         $row = $(row),
         //       $row = $(this);
                flg=true;
                // find only rows with data
                if($row.attr('data-id')){
              
                    export_row = [];
                    
                    checked = $row.find('th input[type=checkbox]').attr("checked");
                    
                    
                    
                    if (checked === "checked"){
                   
            	 
            	 	var curr_data_obj = self.fetchval($row.attr('data-id')).then(function(res){curr_data = res;flg=false;self.loop_data(export_columns_keys,curr_data);});
            	 
                //Model.call('write', [[$row.attr('data-id')], {'price_extra':50}]);
 /*               
start: while(true) {
  if(flg==true) continue start;
  break;
}*/

                 
                     
                        //alert(export_rows);
                        //export_rows.push(export_row);
                        
                     
                    }
                   
                }
                
            });
           
            	
           
            
            
           
        },
        loop_data:function(export_columns_keys_val,curr_data_val){
        export_row = [];
        //alert(export_columns_keys_val);
        //alert(curr_data_val.toSource());
         $.each(export_columns_keys_val,function(){
                            cell = curr_data_val[this];
                               export_row.push(cell);
                        });
                  export_rows.push(export_row);
                  data_count++;
                  if(check_count==data_count)
                  {                  
                  //head_check = $('.oe_list_record_selector:checkbox:checked').length;
		   var self = this;
		    view = this.getParent();
		 $.blockUI();
		    view.session.get_file({
		        url: '/web/export/xls_view',
		        data: {data: JSON.stringify({
		            model : view.model,
		            filename:'Export Carrier Info',
		            headers : export_columns_names,
		            rows : export_rows
		        })},
		        complete: $.unblockUI
		    });
            }
        //return export_row;
        return;
        },
    });

};
