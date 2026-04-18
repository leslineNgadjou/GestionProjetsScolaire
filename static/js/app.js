/**
 * Thème clair / sombre + bascules mot de passe.
 */
(function () {
  var THEME_KEY = 'app-theme';

  function getTheme() {
    return document.documentElement.getAttribute('data-bs-theme') || 'light';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {}
    syncThemeToggleUi();
  }

  function syncThemeToggleUi() {
    var t = getTheme();
    var lightIc = document.querySelector('.app-theme-icon-light');
    var darkIc = document.querySelector('.app-theme-icon-dark');
    if (lightIc && darkIc) {
      lightIc.classList.toggle('d-none', t === 'dark');
      darkIc.classList.toggle('d-none', t !== 'dark');
    }
    var btn = document.getElementById('app-theme-toggle');
    if (btn) {
      btn.setAttribute(
        'aria-label',
        t === 'dark' ? 'Passer au thème clair' : 'Passer au thème sombre',
      );
    }
  }

  function initThemeToggle() {
    var btn = document.getElementById('app-theme-toggle');
    if (!btn || btn.dataset.appThemeWired) {
      return;
    }
    btn.dataset.appThemeWired = '1';
    syncThemeToggleUi();
    btn.addEventListener('click', function () {
      setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    });
  }

  /**
   * Champs entiers strictement positifs (saisie chiffres uniquement, pas de "e" ni "--").
   * Attributs : data-app-digits-only, optionnellement data-app-int-min / data-app-int-max.
   */
  function initDigitsOnlyIntInputs() {
    document.querySelectorAll('[data-app-digits-only]').forEach(function (el) {
      if (el.dataset.appDigitsWired) {
        return;
      }
      el.dataset.appDigitsWired = '1';
      var minV = parseInt(el.getAttribute('data-app-int-min'), 10);
      var maxV = parseInt(el.getAttribute('data-app-int-max'), 10);
      if (Number.isNaN(minV)) minV = 1;
      if (Number.isNaN(maxV)) maxV = 2147483647;

      function stripToDigits() {
        var raw = el.value.replace(/\D/g, '');
        if (raw !== el.value) {
          el.value = raw;
        }
      }

      el.addEventListener('input', stripToDigits);
      el.addEventListener('blur', function () {
        stripToDigits();
        if (el.value === '') {
          return;
        }
        var n = parseInt(el.value, 10);
        if (Number.isNaN(n)) {
          el.value = '';
          return;
        }
        if (n < minV) {
          el.value = String(minV);
        } else if (n > maxV) {
          el.value = String(maxV);
        } else {
          el.value = String(n);
        }
      });
    });
  }

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

  function init() {
    initThemeToggle();
    initDigitsOnlyIntInputs();
    initPasswordToggles();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
