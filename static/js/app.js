document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-alert]").forEach((alert, index) => {
        const closeButton = alert.querySelector(".alert-close");

        const dismiss = () => {
            alert.classList.add("fade-out");
            window.setTimeout(() => alert.remove(), 300);
        };

        if (closeButton) {
            closeButton.addEventListener("click", dismiss);
        }

        window.setTimeout(dismiss, 4500 + index * 350);
    });

    document.querySelectorAll("[data-file-input]").forEach((input) => {
        const display = document.querySelector(`[data-file-display="${input.id}"]`);

        const updateDisplay = () => {
            if (!display) {
                return;
            }

            if (input.files && input.files.length > 0) {
                const file = input.files[0];
                const sizeInKb = Math.max(1, Math.round(file.size / 1024));
                display.textContent = `${file.name} (${sizeInKb} KB)`;
            } else {
                display.textContent = "No file selected";
            }
        };

        input.addEventListener("change", updateDisplay);
        updateDisplay();
    });
});
