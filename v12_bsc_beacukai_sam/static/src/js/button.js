odoo.define('v10_bsc_beacukai.tree_view_button', function (require){
"use strict";
 
 
var core = require('web.core');
var ListView = require('web.ListView');
var QWeb = core.qweb;
var Model = require('web.Model');
 
 
ListView.include({       
     
        render_buttons: function($node) {
        		console.log(this);
        		// alert('anjing');
        		// console.log('kampret');
        		// console.log(this.ViewManager.action.domain);     
                var self = this;
                this._super($node);
                    this.$buttons.find('.export_excel').click(this.proxy('tree_view_action'));
        },
 
        tree_view_action: function () {
        	console.log(this);
	        if (this.ViewManager.action.domain.length>0) {
	        	console.log(this);
	        	// console.log(this.ViewManager.action.domain[0][2]);     
			    new Model('salesperson.wizard')
			 	.call('print_excel2', ["",this.ViewManager.action.domain[0][2],this.ViewManager.action.domain[1][2]])
			 	.done(function(result) {
			 		window.location.href=result.url
			 	})	
	        }else{
	        	alert('Isi tanggal mulai dan tanggal selesai')
	        }           
            
		 }
 
});
 
});