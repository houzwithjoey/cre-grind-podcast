// Speed buttons, skip buttons, and resume-where-you-left-off for the episode player.
(function () {
  var audio = document.querySelector('.player audio');
  if (!audio) return;
  var key = 'cregrind-pos-' + (audio.dataset.slug || '');
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  };
  var saved = parseFloat(store.get(key) || '0');
  if (saved > 5) {
    audio.addEventListener('loadedmetadata', function () {
      if (saved < audio.duration - 10) audio.currentTime = saved;
    }, { once: true });
  }
  var last = 0;
  audio.addEventListener('timeupdate', function () {
    if (Math.abs(audio.currentTime - last) > 5) { last = audio.currentTime; store.set(key, String(Math.floor(last))); }
  });
  document.querySelectorAll('.player [data-skip]').forEach(function (b) {
    b.addEventListener('click', function () { audio.currentTime = Math.max(0, audio.currentTime + parseFloat(b.dataset.skip)); });
  });
  var speeds = document.querySelectorAll('.player [data-speed]');
  var savedSpeed = parseFloat(store.get('cregrind-speed') || '1');
  function setSpeed(s) {
    audio.playbackRate = s; store.set('cregrind-speed', String(s));
    speeds.forEach(function (b) { b.setAttribute('aria-pressed', parseFloat(b.dataset.speed) === s ? 'true' : 'false'); });
  }
  speeds.forEach(function (b) { b.addEventListener('click', function () { setSpeed(parseFloat(b.dataset.speed)); }); });
  setSpeed(savedSpeed);
})();
