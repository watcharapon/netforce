/*
 * Copyright (c) 2012-2015 Netforce Co. Ltd.
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
 * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
 * OR OTHER DEALINGS IN THE SOFTWARE.
 */

var Field=NFView.extend({
    _name: "field"
},{
    make_view: function(options) {
        var name=options.name;
        var model=options.context.model;
        if (!model) throw "No model in context";
        var field=model.get_field(name);
        var type=field.type;
        if (options.view) {
            view_name=options.view;
        } else {
            switch (type) {
                case "char":
                    view_name="field_char";
                    break;
                case "text":
                    view_name="field_text";
                    break;
                case "float":
                    view_name="field_float";
                    break;
                case "decimal":
                    view_name="field_decimal";
                    break;
                case "integer":
                    view_name="field_integer";
                    break;
                case "boolean":
                    view_name="field_boolean";
                    break;
                case "date":
                    view_name="field_date";
                    break;
                case "datetime":
                    view_name="field_datetime";
                    break;
                case "selection":
                    view_name="field_selection";
                    break;
                case "file":
                    view_name="field_file";
                    break;
                case "json":
                    view_name="field_json";
                    break;
                case "many2one":
                    view_name="field_many2one";
                    //view_name="field_many2one_new";
                    break;
                case "one2many":
                    view_name="field_one2many";
                    break;
                case "many2many":
                    view_name="field_many2many";
                    break;
                case "reference":
                    view_name="field_reference";
                    break;
                case "float_range":
                    view_name="field_float_range";
                    break;
                case "integer_range":
                    view_name="field_integer_range";
                    break;
                case "date_range":
                    view_name="field_date_range";
                    break;
                default:
                    throw "Invalid field type: "+type;
            }
        }
        var view_cls=get_view_cls(view_name);
        var view=view_cls.make_view(options);
        return view;
    }
});

Field.register();
