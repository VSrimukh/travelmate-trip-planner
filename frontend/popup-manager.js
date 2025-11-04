class PopupManager {
  constructor() {
    this.currentPopup = null;
  }

  createPopup(config) {
    this.closePopup();

    const overlay = document.createElement("div");
    overlay.className = "popup-overlay";
    overlay.id = "popup-overlay";

    const modal = document.createElement("div");
    modal.className = `popup-modal ${config.type}-popup`;

    const header = document.createElement("div");
    header.className = "popup-header";

    if (config.icon) {
      const icon = document.createElement("div");
      icon.className = "popup-icon";
      icon.innerHTML = config.icon;
      header.appendChild(icon);
    }

    if (config.title) {
      const title = document.createElement("div");
      title.className = "popup-title";
      title.textContent = config.title;
      header.appendChild(title);
    }

    if (config.message) {
      const message = document.createElement("div");
      message.className = "popup-message";
      message.textContent = config.message;
      header.appendChild(message);
    }

    const actions = document.createElement("div");
    actions.className = "popup-actions";

    if (config.buttons) {
      config.buttons.forEach((button) => {
        const btn = document.createElement("button");
        btn.className = `popup-button ${button.class || "button-success"}`;
        btn.textContent = button.text;
        btn.onclick = () => {
          if (button.action) button.action();
          this.closePopup();
        };
        actions.appendChild(btn);
      });
    } else {
      const okBtn = document.createElement("button");
      okBtn.className = "popup-button button-success";
      okBtn.textContent = "OK";
      okBtn.onclick = () => this.closePopup();
      actions.appendChild(okBtn);
    }

    modal.appendChild(header);
    modal.appendChild(actions);
    overlay.appendChild(modal);

    document.body.appendChild(overlay);
    this.currentPopup = overlay;

    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        this.closePopup();
      }
    });

    return overlay;
  }

  closePopup() {
    if (this.currentPopup) {
      if (this.currentPopup.parentNode) {
        this.currentPopup.parentNode.removeChild(this.currentPopup);
      }
      this.currentPopup = null;
    }
  }

  showSuccess(title, message, callback = null) {
    return this.createPopup({
      type: "success",
      icon: "✓",
      title: title,
      message: message,
      buttons: [
        {
          text: "Back to Home",
          class: "button-success",
          action: callback,
        },
      ],
    });
  }

  showError(title, message, callback = null) {
    return this.createPopup({
      type: "error",
      icon: "✗",
      title: title,
      message: message,
      buttons: [
        {
          text: "OK",
          class: "button-error",
          action: callback,
        },
      ],
    });
  }

  showBookingSuccess(bookingData, callback = null) {
    return this.createPopup({
      type: "success",
      icon: "✓",
      title: "Submission Successful!",
      message:
        "Thank you for your submission. We have received your information and will process it shortly. You will receive a confirmation email within the next few minutes.",
      buttons: [
        {
          text: "Back to Home",
          class: "button-success",
          action: () => {
            window.location.href = "main.html";
          },
        },
      ],
    });
  }

  showLoginSuccess(userData) {
    return this.createPopup({
      type: "success",
      icon: "✓",
      title: "Submission Successful!",
      message:
        "Thank you for your submission. We have received your information and will process it shortly. You will receive a confirmation email within the next few minutes.",
      buttons: [
        {
          text: "ok",
          class: "button-success",
          action: () => {
            window.location.href = "closepopup";
          },
        },
      ],
    });
  }

  showValidationError(message) {
    return this.createPopup({
      type: "error",
      icon: "✗",
      title: "Please enter a valid value",
      message: message,
      buttons: [
        {
          text: "OK",
          class: "button-error",
        },
      ],
    });
  }
}

window.popupManager = new PopupManager();

window.showSuccessPopup = (title, message, callback) => {
  return window.popupManager.showSuccess(title, message, callback);
};

window.showBookingPopup = (bookingData, callback) => {
  return window.popupManager.showBookingSuccess(bookingData, callback);
};

window.showErrorPopup = (title, message, callback) => {
  return window.popupManager.showError(title, message, callback);
};

window.showLoginSuccess = (userData) => {
  return window.popupManager.showLoginSuccess(userData);
};

window.showValidationError = (message) => {
  return window.popupManager.showValidationError(message);
};

window.closePopup = () => {
  return window.popupManager.closePopup();
};
