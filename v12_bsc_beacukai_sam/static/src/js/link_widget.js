odoo.define('v10_bsc_beacukai_sam.custom_link_bsc', function(require) {
"use strict";

var ListView = require('web.ListView');
function isDict(v) {
    return typeof v==='object' && v!==null && !(v instanceof Array) && !(v instanceof Date);
}

ListView.List.include(/** @lends instance.web.ListView.List# */{
    row_clicked: function (event) {
        var attrs = this.view.fields_view.arch.attrs;
        var show_child_view = ('show_tree' in attrs) ? JSON.parse(attrs['show_tree']) : false;

        if (show_child_view){
            var record_id = $(event.currentTarget).data('id');

            if (this.view.model == "laporan.pertanggungjawaban.kite"){
                this.view.do_action('v10_bsc_beacukai_kite.action_laporan_pertanggungjawaban_mutasi_line_kite',{additional_context:{
                    mutasi_kite_id:record_id,
                }})
            } else {
                this.view.do_action('v10_bsc_beacukai_sam.action_laporan_pertanggungjawaban_mutasi_line_sam',{additional_context:{
                    mutasi_id:record_id,
                }})
            }
        } else {
            return this._super(event);
        }
    },

});

}); // odoo.define
