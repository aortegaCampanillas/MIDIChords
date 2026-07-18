(function (global) {
  "use strict";

  const LANGUAGE_STORAGE_KEY = "fmc_lang";
  let config = null;
  let lastFocusedElement = null;

  function detectLanguage() {
    const saved = global.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (saved === "es" || saved === "en") return saved;
    const browserLanguage = (global.navigator.language || "en").toLowerCase();
    return browserLanguage.startsWith("es") ? "es" : "en";
  }

  function translationsFor(language) {
    return config?.translations?.[language] || {};
  }

  function applyLanguage(language) {
    const texts = translationsFor(language);
    document.documentElement.lang = language;

    const languageButton = document.getElementById("langBtn");
    if (languageButton) languageButton.textContent = language === "en" ? "ES" : "EN";

    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const value = texts[element.dataset.i18n];
      if (value !== undefined) element.textContent = value;
    });
    document.querySelectorAll("[data-i18n-html]").forEach((element) => {
      const value = texts[element.dataset.i18nHtml];
      if (value !== undefined) element.innerHTML = value;
    });
    document.querySelectorAll("[data-i18n-list]").forEach((element) => {
      const values = texts[element.dataset.i18nList];
      if (Array.isArray(values)) {
        element.replaceChildren(...values.map((value) => {
          const item = document.createElement("li");
          item.textContent = value;
          return item;
        }));
      }
    });

    config?.onLanguageChanged?.(language, texts);
  }

  function toggleLanguage() {
    const next = detectLanguage() === "en" ? "es" : "en";
    global.localStorage.setItem(LANGUAGE_STORAGE_KEY, next);
    applyLanguage(next);
  }

  function openLightbox(source) {
    const lightbox = document.getElementById("lightbox");
    const image = document.getElementById("lightbox-img");
    if (!lightbox || !image) return;
    lastFocusedElement = document.activeElement;
    image.src = source;
    lightbox.classList.add("open");
    lightbox.querySelector("button")?.focus();
  }

  function closeLightbox() {
    const lightbox = document.getElementById("lightbox");
    const image = document.getElementById("lightbox-img");
    if (!lightbox || !image || !lightbox.classList.contains("open")) return;
    lightbox.classList.remove("open");
    image.src = "";
    lastFocusedElement?.focus?.();
  }

  function openFeedback() {
    const modal = document.getElementById("feedbackModal");
    if (!modal) return;
    lastFocusedElement = document.activeElement;
    modal.classList.remove("hidden");
    modal.querySelector("input, textarea, button")?.focus();
  }

  function closeFeedback() {
    const modal = document.getElementById("feedbackModal");
    if (!modal || modal.classList.contains("hidden")) return;
    modal.classList.add("hidden");
    lastFocusedElement?.focus?.();
  }

  async function submitFeedback(event) {
    event.preventDefault();
    const language = detectLanguage();
    const texts = translationsFor(language);
    const submitButton = document.getElementById("fbSubmit");
    const status = document.getElementById("fbStatus");
    const name = document.getElementById("fbName")?.value.trim();
    const email = document.getElementById("fbEmail")?.value.trim();
    const message = document.getElementById("fbMessage")?.value.trim();
    if (!name || !email || !message) {
      if (status) status.textContent = texts.fb_error || "Could not send.";
      return;
    }

    submitButton.disabled = true;
    status.textContent = texts.fb_sending || "Sending…";
    try {
      const response = await global.fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          message,
          mode: config.feedbackMode,
          language,
          page_url: global.location.href,
        }),
      });
      const result = await response.json();
      if (!result?.sent) throw new Error("Feedback was not accepted");
      event.target.reset();
      status.textContent = texts.fb_ok || "Thanks! Message sent.";
    } catch {
      status.textContent = texts.fb_error || "Could not send.";
    } finally {
      submitButton.disabled = false;
    }
  }

  function init(options) {
    config = options;
    document.getElementById("feedbackForm")?.addEventListener("submit", submitFeedback);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeLightbox();
        closeFeedback();
      }
    });
    applyLanguage(detectLanguage());
  }

  global.MidiChordsLanding = {
    applyLanguage,
    closeFeedback,
    closeLightbox,
    detectLanguage,
    init,
    openFeedback,
    openLightbox,
    toggleLanguage,
  };
})(globalThis);
