/**
 * Dialogs of the map page. They replace the dialogs of the browser (alert, confirm, prompt), which look different
 * on every system, and use the same look as the message windows of the main application (dark theme, blue OK button).
 *
 *   await AppDialog.alert(message, title)                -> resolves when the dialog is closed
 *   await AppDialog.confirm(message, title)             -> true (OK) or false (Cancel)
 *   await AppDialog.prompt(message, defaultValue, title) -> the text, or null (Cancel)
 */
const AppDialog = (() => {
  const FOCUSABLE = "input, button";

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function open({ title, message, withInput = false, defaultValue = "", showCancel = false }) {
    return new Promise((resolve) => {
      const previouslyFocused = document.activeElement;

      const backdrop = element("div", "app-dialog-backdrop");
      const dialog = element("div", "app-dialog");
      dialog.setAttribute("role", "dialog");
      dialog.setAttribute("aria-modal", "true");

      const header = element("div", "app-dialog-header");
      header.append(element("span", "app-dialog-icon", "i"), element("span", "app-dialog-title", title));

      const body = element("div", "app-dialog-body");
      body.append(element("div", "app-dialog-message", message));

      let input = null;
      if (withInput) {
        input = element("input", "app-dialog-input");
        input.type = "text";
        input.value = defaultValue;
        body.append(input);
      }

      const footer = element("div", "app-dialog-footer");
      let cancelButton = null;
      if (showCancel) {
        cancelButton = element("button", "app-dialog-btn secondary", "Cancel");
        footer.append(cancelButton);
      }
      const okButton = element("button", "app-dialog-btn primary", "OK");
      footer.append(okButton);

      dialog.append(header, body, footer);
      backdrop.append(dialog);

      function close(result) {
        document.removeEventListener("keydown", onKeyDown, true);
        backdrop.remove();
        if (previouslyFocused && previouslyFocused.focus) previouslyFocused.focus();
        resolve(result);
      }
      const accept = () => close(withInput ? input.value : true);
      const dismiss = () => close(withInput ? null : showCancel ? false : true);

      function onKeyDown(event) {
        if (event.key === "Escape") {
          event.preventDefault();
          event.stopPropagation();
          dismiss();
        } else if (event.key === "Enter" && event.target !== cancelButton) {
          event.preventDefault();
          event.stopPropagation();
          accept();
        } else if (event.key === "Tab") {
          // Keep the focus inside the dialog
          const items = Array.from(dialog.querySelectorAll(FOCUSABLE));
          const first = items[0];
          const last = items[items.length - 1];
          if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
          } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
          }
        }
      }

      okButton.addEventListener("click", accept);
      if (cancelButton) cancelButton.addEventListener("click", dismiss);
      document.addEventListener("keydown", onKeyDown, true);

      document.body.append(backdrop);
      if (input) {
        input.focus();
        input.select();
      } else {
        okButton.focus();
      }
    });
  }

  return {
    alert: (message, title = "Message") => open({ title, message }),
    confirm: (message, title = "Confirmation") => open({ title, message, showCancel: true }),
    prompt: (message, defaultValue = "", title = "Input") =>
      open({ title, message, withInput: true, defaultValue, showCancel: true }),
  };
})();
