import os
import sys

version = "0.7"
new_instance = None
our_module = None

re_src_after_order_end = "(?:limit.*|procedure.*|for update.*|lock in share mode.*|[ \r\n\t]*$)"
re_src_after_order = "(?:[ \r\n\t]" + re_src_after_order_end + ")"
re_src_query_order = "(?is)(.*order[ \r\n\t]+by[ \r\n\t]+)(.*?)([ \r\n\t]*" + re_src_after_order_end + ")"

emmalib_file = os.path.abspath(__file__)
emma_path = os.path.dirname(emmalib_file)

if os.path.isdir("emmalib"):
    # svn dev env
    emma_share_path = "emmalib"
    icons_path = "icons"
    glade_path = emma_share_path
else:
    emma_share_path = os.path.join(sys.prefix, "share/emma/")
    icons_path = os.path.join(emma_share_path, "icons")
    glade_path = os.path.join(emma_share_path, "glade")

last_update = 0
