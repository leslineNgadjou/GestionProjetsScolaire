/**
 * Comportements globaux (accessibilité, formulaires).
 */
(function () {
  function initPasswordToggles() {
    document.querySelectorAll('[data-app-password-toggle]').forEach(function (btn) {
      var targetId = btn.getAttribute('data-app-password-toggle');
      var input = targetId ? document.getElementById(targetId) : null;
      if (!input || btn.dataset.appPwWired) {
        return;
      }
      btn.dataset.appPwWired = '1';
      var iconShow = btn.querySelector('.app-pw-icon-show');
      var iconHide = btn.querySelector('.app-pw-icon-hide');

      btn.addEventListener('click', function () {
        var willShowPlain = input.type === 'password';
        input.type = willShowPlain ? 'text' : 'password';
        btn.setAttribute(
          'aria-label',
          willShowPlain ? 'Masquer le mot de passe' : 'Afficher le mot de passe',
        );
        if (iconShow) {
          iconShow.classList.toggle('d-none', willShowPlain);
        }
        if (iconHide) {
          iconHide.classList.toggle('d-none', !willShowPlain);
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordToggles);
  } else {
    initPasswordToggles();
  }
})();
