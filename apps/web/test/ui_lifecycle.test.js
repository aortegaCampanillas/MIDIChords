const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/ui_lifecycle.js");

const {
  createUiLifecycle,
  bindGlobalUiEvents,
  bindImmediatePress,
  bindModalControls,
} = globalThis.MidiChordsUiLifecycle;

class FakeTarget {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, handler) { this.listeners.set(type, handler); }
  removeEventListener(type, handler) {
    if (this.listeners.get(type) === handler) this.listeners.delete(type);
  }
  dispatch(type, event = {}) { this.listeners.get(type)?.(event); }
}

class FakeClock {
  constructor() { this.next = 1; this.timers = new Map(); }
  setTimeout(handler) { const id = this.next++; this.timers.set(id, handler); return id; }
  clearTimeout(id) { this.timers.delete(id); }
  flush() {
    const pending = Array.from(this.timers.values());
    this.timers.clear();
    pending.forEach((handler) => handler());
  }
}

test("lifecycle mounts and removes DOM listeners", () => {
  const target = new FakeTarget();
  const lifecycle = createUiLifecycle(new FakeClock());
  let calls = 0;
  lifecycle.listen(target, "resize", () => { calls += 1; });

  target.dispatch("resize");
  lifecycle.unmount();
  target.dispatch("resize");

  assert.equal(calls, 1);
  assert.equal(target.listeners.size, 0);
  assert.equal(lifecycle.isMounted(), false);
});

test("lifecycle clock runs mounted timers and cancels timers on unmount", () => {
  const clock = new FakeClock();
  const lifecycle = createUiLifecycle(clock);
  let calls = 0;
  lifecycle.later(() => { calls += 1; }, 10);
  clock.flush();
  assert.equal(calls, 1);

  lifecycle.later(() => { calls += 1; }, 10);
  lifecycle.unmount();
  clock.flush();
  assert.equal(calls, 1);
});

test("global UI events dispatch callbacks and pagehide unmounts all listeners", () => {
  const windowTarget = new FakeTarget();
  const documentTarget = new FakeTarget();
  documentTarget.visibilityState = "hidden";
  const lifecycle = createUiLifecycle(new FakeClock());
  const calls = [];
  bindGlobalUiEvents(lifecycle, {
    windowTarget,
    documentTarget,
    onResize: () => calls.push("resize"),
    onScroll: () => calls.push("scroll"),
    onBlur: () => calls.push("blur"),
    onVisible: () => calls.push("visible"),
  });

  windowTarget.dispatch("resize");
  windowTarget.dispatch("scroll");
  windowTarget.dispatch("blur");
  documentTarget.dispatch("visibilitychange");
  documentTarget.visibilityState = "visible";
  documentTarget.dispatch("visibilitychange");
  windowTarget.dispatch("pagehide");

  assert.deepEqual(calls, ["resize", "scroll", "blur", "visible"]);
  assert.equal(windowTarget.listeners.size, 0);
  assert.equal(documentTarget.listeners.size, 0);
});

test("immediate press handles pointer lifecycle without a duplicate click", () => {
  const clock = new FakeClock();
  const lifecycle = createUiLifecycle(clock);
  const documentTarget = new FakeTarget();
  const button = new FakeTarget();
  button.disabled = false;
  const classes = new Set(["stop-mode"]);
  button.classList = {
    toggle(name, enabled) { enabled ? classes.add(name) : classes.delete(name); },
    remove(name) { classes.delete(name); },
  };
  const calls = [];
  bindImmediatePress(lifecycle, button, () => calls.push("action"), {
    documentTarget,
    highlightWhilePressed: true,
    onPress: () => calls.push("press"),
    onRelease: () => calls.push("release"),
  });

  let prevented = 0;
  button.dispatch("mousedown", {
    type: "mousedown",
    button: 0,
    preventDefault: () => { prevented += 1; },
  });
  assert.deepEqual(calls, ["press"]);
  assert.equal(classes.has("active"), true);
  assert.equal(classes.has("stop-mode"), false);

  documentTarget.dispatch("mouseup");
  button.dispatch("click", { preventDefault: () => { prevented += 1; } });
  assert.deepEqual(calls, ["press", "release"]);
  assert.equal(classes.has("active"), false);
  assert.equal(prevented, 2);

  lifecycle.unmount();
  assert.equal(button.listeners.size, 0);
  assert.equal(documentTarget.listeners.size, 0);
});

test("immediate keyboard click releases and clears its highlight on the lifecycle clock", () => {
  const clock = new FakeClock();
  const lifecycle = createUiLifecycle(clock);
  const button = new FakeTarget();
  const classes = new Set();
  button.classList = {
    toggle(name, enabled) { enabled ? classes.add(name) : classes.delete(name); },
    remove(name) { classes.delete(name); },
  };
  const calls = [];
  bindImmediatePress(lifecycle, button, () => {}, {
    documentTarget: new FakeTarget(),
    highlightWhilePressed: true,
    onPress: () => calls.push("press"),
    onRelease: () => calls.push("release"),
  });

  button.dispatch("click", { preventDefault() {} });
  assert.deepEqual(calls, ["press"]);
  assert.equal(classes.has("active"), true);
  clock.flush();
  assert.deepEqual(calls, ["press", "release"]);
  assert.equal(classes.has("active"), false);
});

test("modal controls open, close, and dismiss only from the backdrop", () => {
  const lifecycle = createUiLifecycle(new FakeClock());
  const modal = new FakeTarget();
  const openButton = new FakeTarget();
  const closeButton = new FakeTarget();
  const calls = [];
  bindModalControls(lifecycle, {
    modal,
    openButton,
    closeButton,
    onOpen: () => calls.push("open"),
    onClose: () => calls.push("close"),
  });

  openButton.dispatch("click");
  modal.dispatch("click", { target: {} });
  modal.dispatch("click", { target: modal });
  closeButton.dispatch("click");
  assert.deepEqual(calls, ["open", "close", "close"]);

  lifecycle.unmount();
  openButton.dispatch("click");
  assert.deepEqual(calls, ["open", "close", "close"]);
  assert.equal(modal.listeners.size, 0);
  assert.equal(openButton.listeners.size, 0);
  assert.equal(closeButton.listeners.size, 0);
});
