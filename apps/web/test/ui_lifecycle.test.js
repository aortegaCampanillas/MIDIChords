const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/ui_lifecycle.js");

const { createUiLifecycle } = globalThis.MidiChordsUiLifecycle;

class FakeTarget {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, handler) { this.listeners.set(type, handler); }
  removeEventListener(type, handler) {
    if (this.listeners.get(type) === handler) this.listeners.delete(type);
  }
  dispatch(type) { this.listeners.get(type)?.(); }
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
