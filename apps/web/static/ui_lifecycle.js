(function initUiLifecycle(global) {
  "use strict";

  function createUiLifecycle(clock = global) {
    const listeners = [];
    const timers = new Set();
    let mounted = true;

    function listen(target, type, handler, options) {
      if (!mounted || !target?.addEventListener) return () => {};
      target.addEventListener(type, handler, options);
      const entry = { target, type, handler, options };
      listeners.push(entry);
      return () => {
        const index = listeners.indexOf(entry);
        if (index >= 0) listeners.splice(index, 1);
        target.removeEventListener(type, handler, options);
      };
    }

    function later(handler, delay) {
      if (!mounted) return null;
      let timer = null;
      timer = clock.setTimeout(() => {
        timers.delete(timer);
        if (mounted) handler();
      }, delay);
      timers.add(timer);
      return timer;
    }

    function cancel(timer) {
      if (timer == null) return;
      timers.delete(timer);
      clock.clearTimeout(timer);
    }

    function unmount() {
      if (!mounted) return;
      mounted = false;
      while (listeners.length) {
        const { target, type, handler, options } = listeners.pop();
        target.removeEventListener(type, handler, options);
      }
      for (const timer of timers) clock.clearTimeout(timer);
      timers.clear();
    }

    return Object.freeze({ listen, later, cancel, unmount, isMounted: () => mounted });
  }

  global.MidiChordsUiLifecycle = Object.freeze({ createUiLifecycle });
})(globalThis);
