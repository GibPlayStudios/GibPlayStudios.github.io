// Bitz interactive preview on gibplay.com/Bitz/.
// The main room is drawn from three layers exported by the app's renderer:
// the room behind Bitz, Bitz (sprite frames), and what stands in front. The
// still picture in the page is shown instead whenever the preview can't run.
(function () {
  "use strict";
  var root = document.querySelector("[data-stage]");
  var data = window.BITZ_STAGE;
  if (!root || !data || !window.HTMLCanvasElement || !window.Promise) return;

  var canvas = root.querySelector("canvas");
  var still = root.querySelector(".stage-frame img");
  var controls = root.querySelector(".stage-controls");
  var status = root.querySelector("[data-stage-status]");
  var label = root.querySelector("[data-stage-label]");
  var words = JSON.parse(root.querySelector("[data-stage-words]").textContent);
  var base = root.getAttribute("data-art");
  var ctx = canvas.getContext("2d");
  if (!ctx) return;

  var W = data.size[0], H = data.size[1];
  var CW = data.cell[0], CH = data.cell[1], AX = data.anchor[0], AY = data.anchor[1];
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var cache = {};
  var heart = new Image();
  heart.src = base + "heart.png";

  // The season follows the month (northern hemisphere, the app's default).
  var month = new Date().getMonth() + 1;
  var season = month <= 2 || month === 12 ? "winter" : month <= 5 ? "spring" : month <= 8 ? "summer" : "autumn";
  var phase = "day";
  var scene = null;          // the scene on screen
  var request = 0;           // the newest scene request; older answers are ignored
  var cat = { x: 80, facing: "r", action: "rest", seq: "sit", started: 0, until: 0, target: 80, step: 0 };
  var hearts = [];           // night only: the app's heart sprite over the sleeping cat
  var stillTimer = 0;        // reduced motion: when a still reaction ends
  var visible = true, running = false, last = 0, clock = 0;

  function load(name) {
    if (!cache[name]) {
      cache[name] = Promise.all(["bg", "fg", "cat"].map(function (layer) {
        return new Promise(function (resolve, reject) {
          var img = new Image();
          img.onload = function () { resolve(img); };
          img.onerror = reject;
          img.src = base + "stage-" + name + "-" + layer + ".png";
        });
      })).then(function (imgs) {
        return { name: name, bg: imgs[0], fg: imgs[1], sheet: imgs[2], meta: data.scenes[name] };
      }, function (error) {
        delete cache[name]; // try again next time
        throw error;
      });
    }
    return cache[name];
  }

  function rand(min, max) { return min + Math.random() * (max - min); }

  function rest(seq) {
    cat.action = "rest";
    cat.seq = seq || ["sit", "sit", "loaf", "groom", "look", "blink"][Math.floor(Math.random() * 6)];
    cat.started = clock;
    cat.until = clock + rand(3, 6.5);
  }

  function walk() {
    var spot = scene.meta.spot[0], target;
    do { target = Math.round(rand(spot - 30, spot + 30)); } while (Math.abs(target - cat.x) < 12);
    var facing = target > cat.x ? "r" : "l";
    cat.target = target;
    cat.action = facing !== cat.facing ? "turn" : "walk";
    cat.facing = facing;
    cat.started = clock;
    cat.until = clock + 0.25;
  }

  function frames(seq) { return scene.meta.sequences[seq] || scene.meta.sequences["sit-" + cat.facing]; }

  function frameAt(seq, t) {
    var list = frames(seq);
    return list[Math.floor(Math.max(0, t) * 4) % list.length];
  }

  function currentFrame() {
    var m = scene.meta, t = clock - cat.started;
    if (phase === "night") return reduce.matches ? m.sequences.sleep[0] : frameAt("sleep", clock);
    if (cat.action === "pet") return reduce.matches ? frames("pet-" + cat.facing)[3] : frameAt("pet-" + cat.facing, t);
    if (reduce.matches) return frames("sit-" + cat.facing)[0];
    if (cat.action === "walk") return frames("walk-" + cat.facing)[Math.floor(cat.step / 2.5) % 4];
    if (cat.action === "turn") return frames("turn-" + cat.facing)[0];
    return frameAt(cat.seq + "-" + cat.facing, t);
  }

  function draw() {
    if (!scene) return;
    var m = scene.meta, frame = currentFrame(), cols = data.columns;
    var x = phase === "night" ? m.spot[0] : Math.round(cat.x);
    ctx.clearRect(0, 0, W, H);
    ctx.drawImage(scene.bg, 0, 0);
    ctx.drawImage(scene.sheet, (frame % cols) * CW, Math.floor(frame / cols) * CH, CW, CH,
      x - AX, m.spot[1] - AY, CW, CH);
    ctx.drawImage(scene.fg, 0, 0);
    if (heart.complete && heart.naturalWidth) {
      hearts.forEach(function (h) {
        var age = Math.max(0, clock - h.born);
        ctx.globalAlpha = reduce.matches ? 1 : Math.max(0, 1 - age / h.life);
        ctx.drawImage(heart, h.x, h.y - (reduce.matches ? 0 : Math.floor(age * 5)));
      });
      ctx.globalAlpha = 1;
    }
  }

  function update(dt) {
    clock += dt;
    hearts = hearts.filter(function (h) { return clock - h.born < h.life; });
    if (phase === "night") return;
    if (cat.action === "walk") {
      var dir = cat.target > cat.x ? 1 : -1;
      var move = Math.min(Math.abs(cat.target - cat.x), 16 * dt);
      cat.x += dir * move;
      cat.step += move;
      if (Math.abs(cat.target - cat.x) < 0.01) rest();
    } else if (cat.action === "turn" && clock >= cat.until) {
      cat.action = "walk"; cat.started = clock;
    } else if (cat.action === "pet" && clock >= cat.until) {
      rest("blink");
    } else if (cat.action === "rest" && clock >= cat.until) {
      if (Math.random() < 0.5) walk(); else rest();
    }
  }

  function tick(now) {
    if (!running) return;
    var dt = last ? Math.min(0.25, (now - last) / 1000) : 0;
    last = now;
    update(dt);
    draw();
    window.requestAnimationFrame(tick);
  }

  function setRunning() {
    var should = visible && !document.hidden && !reduce.matches && !!scene;
    if (should && !running) { running = true; last = 0; window.requestAnimationFrame(tick); }
    if (!should) running = false;
    draw();
  }

  function say(text) { status.textContent = text; }

  function sceneName(s, p) { return words["season_" + s] + " · " + words["phase_" + p]; }

  function press(group, value) {
    root.querySelectorAll("[data-" + group + "]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-" + group) === value));
    });
  }

  function endStillReaction() {
    window.clearTimeout(stillTimer);
    stillTimer = 0;
  }

  // Show the season and time of day the buttons ask for. Only the newest
  // request is applied, so quick clicks never leave an older scene on screen.
  function show(message) {
    var name = season + "-" + phase, mine = ++request;
    press("season", season);
    press("phase", phase);
    root.setAttribute("aria-busy", "true");
    return load(name).then(function (next) {
      if (mine !== request) return;
      var changedPhase = !scene || scene.name.split("-")[1] !== phase;
      scene = next;
      endStillReaction();
      if (changedPhase || phase === "night" || Math.abs(cat.x - next.meta.spot[0]) > 36) {
        cat.x = next.meta.spot[0];
        hearts = [];
        rest("sit");
      }
      label.textContent = sceneName(season, phase);
      canvas.setAttribute("aria-label", words["scene_" + phase].replace("{scene}", sceneName(season, phase)));
      root.removeAttribute("aria-busy");
      if (message) say(message);
      setRunning();
    }, function (error) {
      if (mine !== request) return;
      root.removeAttribute("aria-busy");
      if (!scene) throw error;
      // Keep the scene that is showing and put the buttons back to match it.
      season = scene.name.split("-")[0];
      phase = scene.name.split("-")[1];
      press("season", season);
      press("phase", phase);
      say(words.load_error);
    });
  }

  function pet() {
    if (!scene) return;
    var m = scene.meta;
    if (phase === "day") {
      // One reaction at a time: petting again keeps the same purr going a little longer.
      if (cat.action !== "pet") { cat.action = "pet"; cat.started = clock; }
      cat.until = clock + 2.6;
      say(words.pet_day);
    } else {
      if (hearts.length < 4) {
        hearts.push({ x: m.spot[0] - 3, y: m.spot[1] - 20, born: clock, life: 1.8 });
        hearts.push({ x: m.spot[0] + 4, y: m.spot[1] - 24, born: clock + 0.3, life: 1.8 });
      }
      say(words.pet_night);
    }
    if (reduce.matches) {
      // No animation: show the reaction as a still, then settle again.
      endStillReaction();
      if (phase === "night") hearts.forEach(function (h) { h.born = clock; });
      stillTimer = window.setTimeout(function () {
        stillTimer = 0;
        hearts = [];
        if (phase === "day") rest("sit");
        draw();
      }, 2000);
    }
    draw();
  }

  root.addEventListener("click", function (event) {
    var button = event.target.closest("button");
    if (!button || !root.contains(button)) return;
    if (button.hasAttribute("data-pet")) { pet(); return; }
    if (button.hasAttribute("data-phase")) {
      if (button.getAttribute("data-phase") === phase) return;
      phase = button.getAttribute("data-phase");
      show(words["now_" + phase]);
    } else if (button.hasAttribute("data-season")) {
      if (button.getAttribute("data-season") === season) return;
      season = button.getAttribute("data-season");
      show(words.season_now.replace("{season}", words["season_" + season]));
    }
  });

  // Tapping or clicking Bitz pets them; the rest of the picture scrolls as usual.
  canvas.addEventListener("click", function (event) {
    if (!scene) return;
    var box = canvas.getBoundingClientRect();
    var x = (event.clientX - box.left) / box.width * W;
    var y = (event.clientY - box.top) / box.height * H;
    var cx = phase === "night" ? scene.meta.spot[0] : cat.x;
    if (Math.abs(x - cx) < 18 && y > scene.meta.spot[1] - 34 && y < scene.meta.spot[1] + 8) pet();
  });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      setRunning();
    }, { threshold: 0.05 }).observe(root.querySelector(".stage-frame"));
  }
  document.addEventListener("visibilitychange", setRunning);
  var onMotionChange = function () {
    endStillReaction();
    hearts = [];
    if (scene) { cat.x = scene.meta.spot[0]; rest("sit"); }
    setRunning();
  };
  if (reduce.addEventListener) reduce.addEventListener("change", onMotionChange);
  else if (reduce.addListener) reduce.addListener(onMotionChange);

  rest("sit");
  show().then(function () {
    root.classList.add("is-live");
    canvas.hidden = false;
    still.hidden = true;
    controls.hidden = false;
    // Fetch the other scenes in the background so switching is instant.
    window.setTimeout(function () {
      ["winter", "spring", "summer", "autumn"].forEach(function (s) {
        ["day", "night"].forEach(function (p) { load(s + "-" + p).catch(function () {}); });
      });
    }, 1200);
  }).catch(function () {
    say(words.preview_error);
  });
})();
