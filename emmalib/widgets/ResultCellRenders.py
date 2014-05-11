
def render_mysql_string(column, cell, model, _iter, _id):
    o = model.get_value(_iter, _id)
    if not o is None:
        cell.set_property("foreground", None)
        cell.set_property("background", None)
        cell.set_property("text", o)
        cell.set_property("editable", True)
        # if len(o) < 256:
        #     cell.set_property("text", o)
        #     cell.set_property("editable", True)
        # else:
        #     cell.set_property("text", o[0:256] + "...")
        #     cell.set_property("editable", False)
    else:
        # cell.set_property("background", self.config.get("null_color"))
        cell.set_property("foreground", "#888888")
        cell.set_property("text", "<null>")
        cell.set_property("editable", True)