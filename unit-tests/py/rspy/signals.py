# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2025 Intel Corporation. All Rights Reserved.

from rspy import log
import sys, signal, inspect


# brainstem is overriding our signal, we use this to block it
def block_brainstem_signals():
    _real_signal = signal.signal
    def guarded_signal(sig, handler):
        # walk the call stack
        for frm in inspect.stack():
            module = frm.frame.f_globals.get("__name__", "")
            # if any frame originates in BrainStem, ignore it
            if module.startswith("brainstem._link"):
                return None
        # otherwise install as normal
        return _real_signal(sig, handler)

    signal.signal = guarded_signal


signal_handler = lambda: log.d("Signal handler not set")


def register_signal_handlers(on_signal=None):
    def handle_abort(signum, _):
        global signal_handler
        log.w("got signal", signum, "aborting... ")
        signal_handler()
        sys.exit(1)

    global signal_handler
    signal_handler = on_signal or signal_handler

    signal.signal(signal.SIGTERM, handle_abort)  # for when aborting via Jenkins
    signal.signal(signal.SIGINT, handle_abort)  # for Ctrl+C
