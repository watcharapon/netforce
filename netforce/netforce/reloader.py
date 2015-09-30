# Copyright (c) 2012-2015 Netforce Co. Ltd.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

try:
    import pyinotify
except:
    print("WARNING: failed to import pyinotify")
from . import static
import sys
import os
from . import module
from multiprocessing import Process

try:
    class EventHandler(pyinotify.ProcessEvent):

        def process_IN_CREATE(self, event):
            if event.pathname.endswith(".xml"):
                static.clear_js()

        def process_IN_DELETE(self, event):
            if event.pathname.endswith(".xml"):
                static.clear_js()

        def process_IN_MODIFY(self, event):
            if event.pathname.endswith(".xml"):
                static.clear_js()
except:
    pass


def listen_changes():
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    loaded_modules = module.get_loaded_modules()
    for m in loaded_modules:
        mod_path = os.path.dirname(sys.modules[m].__file__)
        action_path = os.path.join(mod_path, "actions")
        if os.path.exists(action_path):
            wm.add_watch(action_path, mask)
        view_path = os.path.join(mod_path, "views")
        if os.path.exists(view_path):
            wm.add_watch(view_path, mask)
    print("watching changes...")
    notifier.loop()


def start_reloader():
    p = Process(target=listen_changes)
    p.start()
