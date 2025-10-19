document.addEventListener('DOMContentLoaded', () => {

  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  // Add a click event on each of them
  $navbarBurgers.forEach( el => {
    el.addEventListener('click', () => {

      // Get the target from the "data-target" attribute
      const target = el.dataset.target;
      const $target = document.getElementById(target);

      // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
      el.classList.toggle('is-active');
      $target.classList.toggle('is-active');

    });
  });

});

// Looks for all notifications with a delete and allows closing them when pressing delete
document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.notification .delete:not(.js-delete-excluded)') || []).forEach(($delete) => {
    const $notification = $delete.parentNode;

    $delete.addEventListener('click', () => {
      $notification.parentNode.removeChild($notification);
    });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.message .delete') || []).forEach(($delete) => {
    $delete.addEventListener('click', () => {
      const message = $delete.closest('.message');
      if (message) {
        message.remove();
      }
    });
  });
  // DROPDOWNS
  const $clickableDropdowns = document.querySelectorAll(
    ".dropdown:not(.is-hoverable)",
  );

  if ($clickableDropdowns.length > 0) {
    $clickableDropdowns.forEach(($dropdown) => {
      if (!$dropdown.querySelector("button")) {
        return;
      }

      $dropdown.querySelector("button").addEventListener("click", (event) => {
        event.stopPropagation();
        $dropdown.classList.toggle("is-active");
      });
    });

    document.addEventListener("click", () => {
      closeDropdowns();
    });
  }

  function closeDropdowns() {
    $clickableDropdowns.forEach(($el) => {
      $el.classList.remove("is-active");
    });
  }

  // MODALS //

  function openModal($el) {
        $el.classList.add('is-active');
        send("Modal.open", {
            modal: $el.id
        });
    }

    function closeModal($el) {
        $el.classList.remove('is-active');
    }

    function closeAllModals() {
        (document.querySelectorAll('.modal') || []).forEach(($modal) => {
            closeModal($modal);
        });
    }

    // Add a click event on buttons to open a specific modal
    (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {
        const modal = $trigger.dataset.target;
        const $target = document.getElementById(modal);

        $trigger.addEventListener('click', () => {
            openModal($target);
        });
    });

    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .modal-close, .delete, .nf-modal-close') || []).forEach(($close) => {
        const $target = $close.closest('.modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeAllModals();
        }
    });
});


