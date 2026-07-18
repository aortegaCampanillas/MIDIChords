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

  function bindGlobalUiEvents(lifecycle, options) {
    const windowTarget = options.windowTarget;
    const documentTarget = options.documentTarget;
    lifecycle.listen(windowTarget, "resize", options.onResize);
    lifecycle.listen(windowTarget, "scroll", options.onScroll, true);
    lifecycle.listen(windowTarget, "blur", options.onBlur);
    lifecycle.listen(documentTarget, "visibilitychange", () => {
      if (documentTarget.visibilityState === "visible") options.onVisible();
    });
    lifecycle.listen(windowTarget, "pagehide", () => lifecycle.unmount());
  }

  function bindImmediatePress(lifecycle, button, action, options = {}) {
    if (!button || typeof action !== "function") return;
    const documentTarget = options.documentTarget || global.document;
    const highlightWhilePressed = !!options.highlightWhilePressed;
    const onPress = typeof options.onPress === "function" ? options.onPress : null;
    const onRelease = typeof options.onRelease === "function" ? options.onRelease : null;
    let suppressNextClick = false;
    let pointerPressed = false;

    const setPressedVisual = (pressed) => {
      if (!highlightWhilePressed) return;
      button.classList.toggle("active", !!pressed);
      if (pressed) button.classList.remove("stop-mode");
    };

    const onPointerStart = (event) => {
      if (button.disabled) return;
      if (event.type === "mousedown" && Number(event.button) !== 0) return;
      event.preventDefault();
      suppressNextClick = true;
      pointerPressed = true;
      setPressedVisual(true);
      if (onPress) onPress();
      else action();
    };

    const onPointerEnd = () => {
      if (!pointerPressed) return;
      pointerPressed = false;
      setPressedVisual(false);
      if (onRelease) onRelease();
    };

    lifecycle.listen(button, "mousedown", onPointerStart);
    lifecycle.listen(button, "touchstart", onPointerStart, { passive: false });
    lifecycle.listen(documentTarget, "mouseup", onPointerEnd);
    lifecycle.listen(documentTarget, "touchend", onPointerEnd, { passive: true });
    lifecycle.listen(documentTarget, "touchcancel", onPointerEnd, { passive: true });
    lifecycle.listen(button, "click", (event) => {
      if (button.disabled) {
        event.preventDefault();
        return;
      }
      if (suppressNextClick) {
        suppressNextClick = false;
        event.preventDefault();
        return;
      }
      if (onPress) {
        onPress();
        if (onRelease) lifecycle.later(onRelease, 140);
      } else {
        action();
      }
      if (highlightWhilePressed) {
        setPressedVisual(true);
        lifecycle.later(() => setPressedVisual(false), 140);
      }
    });
  }

  function bindModalControls(lifecycle, options) {
    const modal = options.modal;
    if (options.openButton && typeof options.onOpen === "function") {
      lifecycle.listen(options.openButton, "click", options.onOpen);
    }
    if (options.closeButton && typeof options.onClose === "function") {
      lifecycle.listen(options.closeButton, "click", options.onClose);
    }
    if (modal && typeof options.onClose === "function") {
      lifecycle.listen(modal, "click", (event) => {
        if (event.target === modal) options.onClose();
      });
    }
  }

  global.MidiChordsUiLifecycle = Object.freeze({
    createUiLifecycle,
    bindGlobalUiEvents,
    bindImmediatePress,
    bindModalControls,
  });
})(globalThis);
