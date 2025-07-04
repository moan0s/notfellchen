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
  (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
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
});


