odoo.define('th_dynamic_list.DynamicList', function(require) {

    "use strict";
    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var fieldRegistry = require('web.field_registry');
    var QWeb = core.qweb;
    var uid = session.uid;
    var _t = core._t;

    ListView.include({
		init: function (viewInfo, params) {
            this._super.apply(this, arguments);
			var arch = viewInfo.arch;
			this.rendererParams.arch.view_id = viewInfo.view_id;
			var self=this;
			rpc.query({
                model: 'th.fields',
                method: 'has_access',
                args: [],
            }).then(function(result){
                self.controllerParams['has_access'] = result;
            });
        },
	});

    ListController.include({

        init: function (parent, model, renderer, params) {
        	var self = this;
            this.stopBanner = true;
            this.has_access = params.has_access;
			this._super.apply(this, arguments);
			var domain = [['view_id', '=', self.renderer.arch.view_id], ['user_id', '=', uid]];
            var fields = ['th_list_text'];
            this.default_arch = renderer.arch.children;
            this.default_list = [];
            for(var i in renderer.arch.children){
                this.default_list.push(renderer.arch.children[i].attrs.name);
            }
        	rpc.query({
                model: 'th.fields',
                method: 'search_read',
                args: [domain, fields],
            }).then(function(result){
            	if(result.length > 0){
            		self.col_list = _.filter(JSON.parse(result[0].th_list_text), function(elem){return elem.visible});
					var sortArray = _.pluck(self.col_list, 'name');
                    _.each(self.renderer.arch.children, function(elm){
                        if (!_.contains(sortArray, elm.attrs.name)){
                            elm.attrs.modifiers= '{"tree_invisible": true}';
                        }
                    });
                    sortArray = _.compact(sortArray);
					self.render_fields(sortArray);
				}
			}).done(function (){self.stopBanner = false;});
            var col_values = this.prepare_col_vals();
            self.$DColumns = $(QWeb.render("ListviewColumns",{'columns': col_values}));
			self.$DColumns.find('.th_ul').click(function (e) {
				e.stopPropagation();
            });
            self.$DColReset = $(QWeb.render("th_list_reset",{}));
        },

        _renderBanner: function () {
            if (this.stopBanner){return $.when();}
            else{return this._super.apply(this, arguments);}
        },

        fetch_invisible_fields: function(){
            // TODO: Invisble fields are not added to the arch
			var self = this;
        	this.invisible_fields = {};
        	this.invisible_field_names = [];
        	for(var i in self.renderer.arch.children){
        		var modifiers = self.renderer.arch.children[i].attrs.modifiers;
        		if(modifiers.column_invisible){
        			this.invisible_fields[self.renderer.arch.children[i].attrs.name] = self.renderer.arch.children[i];
        			this.invisible_field_names.push(self.renderer.arch.children[i].attrs.name);
        		}
            }
        },

        prepare_col_vals: function(){
        	var self = this;
        	var col_vals = [];
        	_.each(_.pairs(this.renderer.state.fields), function(field){
        	    if (field[1].type != 'many2many' && field[1].type != 'one2many'){
	        		col_vals.push({string: field[1].string, name: field[0]});
	        	}
        	});
        	return col_vals;
        },

        precheck_li: function(){
        	var self = this;
        	var seq = 0;
        	self.col_list = [];
//        	self.default_list = [];
        	self.$DColumns.find('.columnCheckbox').removeAttr('checked');
        	for(var i in self.renderer.columns){
                self.$DColumns.find("#" + self.renderer.columns[i].attrs.name).prop('checked',true).attr('data-seq', seq);
                self.col_list.push({'name': self.renderer.columns[i].attrs.name, 'visible': true, 'seq': seq});
//                self.default_list.push(self.renderer.columns[i].attrs.name);
                seq = seq + 1;
            }
        	return seq;
        },

        sort_elements: function(){
        	var self = this;
			var elems = self.$DColumns.find('.th_ul #dycollist');
			elems.sort(function(a, b) {
			    if (parseInt($(a).find('input').attr('data-seq')) < parseInt($(b).find('input').attr('data-seq')))
			    return -1;
			    if (parseInt($(a).find('input').attr('data-seq')) > parseInt($(b).find('input').attr('data-seq')))
			    return 1; return 0;
			}).appendTo(elems.parent());
		},

        renderSidebar: function ($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (self.$DColumns && ! _.isUndefined($node) && self.has_access){
                $node.append(self.$DColumns);
                self.$DColumns.find('.th_ul li:first-child').after(self.$DColReset);
                this.col_list = [];
				var seq = self.precheck_li() - 1;
				self.sort_elements();

				self.$DColumns.find('.th_ul #dycollist').each(function(){
					$(this).attr('data-search-term', $(this).find('#ld').text().toLowerCase());
				});

				self.$DColumns.find("#dycolsrch").on('keyup', function(){
					var searchTerm = $(this).val().toLowerCase();
					$('.th_ul #dycollist').each(function(){
				        if ($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) {
				            $(this).show();
				        } else {
				            $(this).hide();
				        }
				    });
				});

				self.$DColumns.find('.th_ul').sortable({
				     cancel: ".no-sort",
				     placeholder: "ui-state-highlight",
				     axis: "y",
				     items: "li:not(.no-sort)",
				     update : function( event, ul) {
				         $('.th_ul #dycollist').each(function(i){
				            $(this).find('input').attr('data-seq', i);
				            //updates the self.col_list sequence
				            var input_name = $(this).find('input').attr('name');
				            var col_field = _.find(self.col_list, function(item){
				            	return item.name == input_name;
				            });
				            if (col_field !== undefined ){col_field.seq = i};
				         });
				         self.col_list = _.sortBy(self.col_list, function(o) { return o.seq;});
				         var col_names = [];
				         $('#dycollist input:checked').each(function() {
				        	 col_names.push($(this).attr('name'));
				         });
				         //push only checked data
				         self.render_fields(col_names);
				     },
				});


				self.$DColumns.find('.columnCheckbox').change(function (e){
		        	var val_checked = $("#"+this.id).prop("checked");
		        	if (val_checked){
		        		seq = seq + 1;
		        		var id_search = _.findWhere(self.col_list,{name:this.id});
		        		if (id_search === undefined){
		        			self.col_list.push({'name':this.id,'visible':true,'seq':seq});
		        		}else{id_search.visible = true;id_search.seq = seq;}
		        	}
		        	else{
		        		var id_search = _.findWhere(self.col_list,{name:this.id});
		        		if (typeof id_search === undefined){
		        			self.col_list.push({'name':this.id,'visible':false,'seq':100});
		        		}else{id_search.visible = false;id_search.seq = 100;}
		        	}

		        	self.col_list = _.sortBy(self.col_list, function(o) { return o.seq;});
		        	var col_names = _.pluck(self.col_list, 'name');
		        	self.sort_elements();
		        	self.render_fields(col_names);
		        });

				self.$DColumns.find('#restoreList').click(function(e){
					rpc.query({
						model: 'th.fields',
						method: 'search',
						args: [[["view_id", "=", self.renderer.arch.view_id],["user_id", "=", uid]]],
					}).then(function(result){
					    if(result.length > 0){
                            rpc.query({
                                model: 'th.fields',
                                method: 'unlink',
                                args: result,
                            }).then(function(e){
                                location.reload();
                            })
						}
					});
				});
// TODO
				self.$DColumns.find("#editableToggler").change(function() {
				    if(this.checked) {
                        self.editable = true;
                        self.mode = "edit";
                        self.renderer.editable = true;
                        $(this).parent().addClass('active');
                    }
                    else{
                        self.editable = false;
                        self.mode = "readonly";
                        self.renderer.editable = false;
                        $(this).parent().removeClass('active');
                    }
                    self.reload();
                });
            }
        },

        render_fields: function(col_names){
            // TODO: Uncaught TypeError: Widget is not a constructor
			var self = this;
			self.fetch_invisible_fields();
			self.renderer.arch.children = [];
			self.renderer.fields = {};
			var child_count = 0;
			for(var i in col_names){
				var cname = col_names[i];
				var search_col = _.findWhere(self.col_list,{name: cname});
				if(search_col.visible == true){
//				    var col_modifiers = {readonly:self.initialState.fields[cname].readonly,
//                                    required:self.initialState.fields[cname].required,
//                                    column_invisible:false};
//                    if (_.has(self.initialState.fieldsInfo.list, cname) && self.initialState.fieldsInfo.list[cname].modifiers){
//                        col_modifiers = self.initialState.fieldsInfo.list[cname].modifiers;
//                        col_modifiers.column_invisible = false;
//                    }
                    if (cname && $.inArray(cname, self.default_list) != -1){
                        for(var i in self.default_arch){
                            if (cname == self.default_arch[i].attrs.name){
                                self.renderer.arch.children.push(self.default_arch[i]);
                                if( typeof self.renderer.arch.children[child_count].attrs.modifiers == "string" ){
                                    self.renderer.arch.children[child_count].attrs.modifiers = {"column_invisible": false};
                                } else {
                                    self.renderer.arch.children[child_count].attrs.modifiers['column_invisible'] = false;
                                }
                            }
                        }
                    }
                    else{
                        self.renderer.arch.children.push({
                            attrs:{
                                modifiers: {},
                                name: cname,
                            },
                            children: [],
                            tag: 'field'
                        });
					}
				}
				else if(cname && $.inArray(cname, self.default_list) != -1){
				    for(var i in self.default_arch){
                        if (cname == self.default_arch[i].attrs.name){
                            self.renderer.arch.children.push(self.default_arch[i]);
                            if( typeof self.renderer.arch.children[child_count].attrs.modifiers == "string" ){
                                self.renderer.arch.children[child_count].attrs.modifiers = {"column_invisible": true};
                            } else {
                                self.renderer.arch.children[child_count].attrs.modifiers['column_invisible'] = true;
                            }
                        }
                    }
//				    col_modifiers.column_invisible = true;
//					self.renderer.arch.children.push({
//						attrs:{
//							modifiers: col_modifiers,
//							name: cname,
//						},
//						children: [],
//						tag: 'field'
//					});
				}
				child_count += 1;
			}
            // //FIXME : invisble fields are not added to the arch
        	// for(var i in self.invisible_field_names){
        	// 	self.renderer.arch.children.push(self.invisible_fields[self.invisible_field_names[i]]);
        	// 	if (this.id){
        	// 		self.col_list.push({'name':this.id,'visible':false,'seq':100});
				// }
        	// }
            for(var i in col_names){
				var cname = col_names[i];
				var search_col = _.findWhere(self.col_list,{name: cname});
				if(search_col.visible == true){
				    if(self.renderer.state.fieldsInfo.list[cname]){
				        self.renderer.state.fieldsInfo.list[cname].invisible = "0"
				    }else{
				        var ftype = self.renderer.state.fields[cname].type;
				        var FieldWidget = fieldRegistry.getAny(['list.' + ftype, ftype]);
                        self.renderer.state.fieldsInfo.list[cname] = {
                            name: cname,
                            invisible: "0",
                            Widget: FieldWidget,
                            options: {},
                        }
                    }
				}
				else if(cname && $.inArray(cname, self.default_list))
				{
				    if(self.renderer.state.fieldsInfo.list[cname]){
				        self.renderer.state.fieldsInfo.list[cname].invisible = "1"
				    }
				}
			}

            self.renderer._processColumns({});
            self.precheck_li();
            self.sort_elements();
            self.reload();
            self.store_current_state();
		},

		store_current_state: function(){
			var self=this;
			self.col_list = _.filter(self.col_list,function (value) {
			    return value.name !==null;
			})
			self.col_list = _.filter(self.col_list,function (value) {
			    return typeof value.name != 'undefined';
			})
			// TODO: add limit and order by for multiple list views.
			// add functionatily to manage the list view by storing the list and user can access it.
			rpc.query({
                model: 'th.fields',
                method: 'search',
                args: [[["view_id", "=", self.renderer.arch.view_id],["user_id", "=", uid]]],
            }).then(function(results){
				if(results.length==1){
					rpc.query({
						model: 'th.fields',
						method: 'write',
						args: [results, {'th_list_text': JSON.stringify(self.col_list)}],
					})
        		}else{
					rpc.query({
						model: 'th.fields',
						method: 'create',
						args: [{
							'view_id': self.renderer.arch.view_id,
							'th_list_text': JSON.stringify(self.col_list),
							'user_id': uid
						}],
					})
        		}
			})
		},
    })

});