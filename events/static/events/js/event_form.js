// static/ivents/js/event_form.js
document.addEventListener("DOMContentLoaded", function () {
  // ---------- PREVIEW THUMBNAIL ----------
  const thumbnailInput = document.getElementById("id_thumbnail");
  const previewImg = document.getElementById("thumbnail-preview");

  if (thumbnailInput && previewImg) {
    thumbnailInput.addEventListener("change", function () {
      const file = this.files && this.files[0];
      if (!file) {
        previewImg.src = "";
        previewImg.classList.add("d-none");
        return;
      }

      const reader = new FileReader();
      reader.onload = function (e) {
        previewImg.src = e.target.result;
        previewImg.classList.remove("d-none");
      };
      reader.readAsDataURL(file);
    });
  }

  // ---------- VALIDACIÓ MÀXIM ESPECTADORS ----------
  const maxViewersInput = document.getElementById("id_max_viewers");

  if (maxViewersInput) {
    const validateMaxViewers = function () {
      const value = parseInt(maxViewersInput.value, 10);

      if (isNaN(value)) {
        maxViewersInput.setCustomValidity("");
        maxViewersInput.classList.remove("is-invalid");
        return;
      }

      if (value < 1 || value > 1000) {
        maxViewersInput.setCustomValidity(
          "El màxim d'espectadors ha d'estar entre 1 i 1000."
        );
        maxViewersInput.classList.add("is-invalid");
      } else {
        maxViewersInput.setCustomValidity("");
        maxViewersInput.classList.remove("is-invalid");
      }
    };

    maxViewersInput.addEventListener("input", validateMaxViewers);
    maxViewersInput.addEventListener("blur", validateMaxViewers);
  }

  // ---------- VALIDACIÓ DATA PROGRAMADA ----------
  const scheduledDateInput = document.getElementById("id_scheduled_date");

  if (scheduledDateInput) {
    const validateScheduledDate = function () {
      const value = scheduledDateInput.value;
      if (!value) {
        scheduledDateInput.setCustomValidity("");
        scheduledDateInput.classList.remove("is-invalid");
        return;
      }

      const entered = new Date(value);
      const now = new Date();

      if (entered < now) {
        scheduledDateInput.setCustomValidity(
          "La data programada no pot ser en el passat."
        );
        scheduledDateInput.classList.add("is-invalid");
      } else {
        scheduledDateInput.setCustomValidity("");
        scheduledDateInput.classList.remove("is-invalid");
      }
    };

    scheduledDateInput.addEventListener("change", validateScheduledDate);
    scheduledDateInput.addEventListener("input", validateScheduledDate);
    scheduledDateInput.addEventListener("blur", validateScheduledDate);
  }

  // ---------- VALIDACIÓ DEL TÍTOL ----------
  const titleInput = document.getElementById("id_title");
  if (titleInput) {
    const validateTitle = function () {
      if (!titleInput.value.trim()) {
        titleInput.setCustomValidity("El títol és obligatori.");
        titleInput.classList.add("is-invalid");
      } else {
        titleInput.setCustomValidity("");
        titleInput.classList.remove("is-invalid");
      }
    };
    titleInput.addEventListener("input", validateTitle);
    titleInput.addEventListener("blur", validateTitle);
  }

  // ---------- VALIDACIÓ STREAM URL ----------
  const streamInput = document.getElementById("id_stream_url");
  if (streamInput) {
    const validateStreamUrl = function () {
      const value = streamInput.value.trim();
      if (!value) {
        streamInput.setCustomValidity("");
        streamInput.classList.remove("is-invalid");
        return;
      }

      const isYoutube =
        value.includes("youtube.com") || value.includes("youtu.be");
      const isTwitch = value.includes("twitch.tv");

      if (!isYoutube && !isTwitch) {
        streamInput.setCustomValidity(
          "Introdueix una URL de YouTube o Twitch vàlida."
        );
        streamInput.classList.add("is-invalid");
      } else {
        streamInput.setCustomValidity("");
        streamInput.classList.remove("is-invalid");
      }
    };

    streamInput.addEventListener("input", validateStreamUrl);
    streamInput.addEventListener("blur", validateStreamUrl);
  }
});
