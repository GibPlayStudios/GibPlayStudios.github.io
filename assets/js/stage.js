// Bitz demo stage for gibplay.com/Bitz/.
// Draws the main room from three layers exported by the app's renderer
// (behind Bitz, Bitz, in front) on a 160 x 112 canvas. Without JavaScript the
// page shows a still picture of the same room instead. This is a website demo:
// it isn't connected to anyone's cat or save.
(function () {
  "use strict";
  var root = document.querySelector("[data-stage]");
  var data = window.BITZ_STAGE;
  if (!root || !data || !window.HTMLCanvasElement) return;

  var canvas = root.querySelector("canvas");
  var still = root.querySelector(".stage-frame img");
  var controls = root.querySelector(".stage-controls");
  var status = root.querySelector("[data-stage-status]");
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

  // Season follows the month (northern hemisphere, as the app's default).
  var month = new Date().getMonth() + 1;
  var season = month <= 2 || month === 12 ? "winter" : month <= 5 ? "spring" : month <= 8 ? "summer" : "autumn";
  var phase = "day";
  var scene = null;

  var cat = { x: 80, facing: "r", action: "rest", seq: "sit", started: 0, until: 0, target: 80, step: 0 };
  var hearts = [];
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
      });
    }
    return cache[name];
  }

  function rand(min, max) { return min + Math.random() * (max - min); }

  function rest(now, seq) {
    cat.action = "rest";
    cat.seq = seq || ["sit", "sit", "loaf", "groom", "look", "blink"][Math.floor(Math.random() * 6)];
    cat.started = now;
    cat.until = now + rand(3, 6.5);
  }

  function walk(now) {
    var spot = scene.meta.spot[0], target;
    do { target = Math.round(rand(spot - 34, spot + 34)); } while (Math.abs(target - cat.x) < 14);
    var facing = target > cat.x ? "r" : "l";
    cat.target = target;
    cat.action = facing !== cat.facing ? "turn" : "walk";
    cat.facing = facing;
    cat.started = now;
    cat.until = now + 0.25;
  }

  function frameOf(seq, t, fps) {
    var frames = scene.meta.sequences[seq];
    if (!frames) return 0;
    return frames[Math.floor(t * fps) % frames.length];
  }

  function draw() {
    if (!scene) return;
    var m = scene.meta, frame, x;
    ctx.clearRect(0, 0, W, H);
    ctx.drawImage(scene.bg, 0, 0);
    if (phase === "night") {
      frame = reduce.matches ? m.sequences.sleep[0] : frameOf("sleep", clock, 4);
      x = m.spot[0];
    } else {
      var t = clock - cat.started;
      if (reduce.matches) frame = m.sequences[(cat.action === "pet" ? "pet-" : "sit-") + cat.facing][cat.action === "pet" ? 4 : 0];
      else if (cat.action === "walk") frame = m.sequences["walk-" + cat.facing][Math.floor(cat.step / 2.5) % 4];
      else if (cat.action === "turn") frame = m.sequences["turn-" + cat.facing][0];
      else if (cat.action === "pet") frame = frameOf("pet-" + cat.facing, t, 4);
      else frame = frameOf(cat.seq + "-" + cat.facing, t, 4);
      x = Math.round(cat.x);
    }
    var cols = data.columns;
    ctx.drawImage(scene.sheet, (frame % cols) * CW, Math.floor(frame / cols) * CH, CW, CH,
      x - AX, m.spot[1] - AY, CW, CH);
    ctx.drawImage(scene.fg, 0, 0);
    if (heart.complete) {
      hearts.forEach(function (h) {
        var age = clock - h.born;
        var rise = reduce.matches ? 0 : Math.floor(age * 6);
        ctx.globalAlpha = Math.max(0, 1 - age / h.life * 0.7);
        ctx.drawImage(heart, Math.round(h.x), Math.round(h.y - rise));
      });
      ctx.globalAlpha = 1;
    }
  }

  function update(dt) {
    clock += dt;
    hearts = hearts.filter(function (h) { return clock - h.born < h.life; });
    if (phase === "night" || !scene) return;
    if (cat.action === "walk") {
      var dir = cat.target > cat.x ? 1 : -1;
      var move = Math.min(Math.abs(cat.target - cat.x), 16 * dt);
      cat.x += dir * move;
      cat.step += move;
      if (Math.abs(cat.target - cat.x) < 0.01) rest(clock);
    } else if (cat.action === "turn" && clock >= cat.until) {
      cat.action = "walk"; cat.started = clock;
    } else if (cat.action === "pet" && clock >= cat.until) {
      rest(clock, "blink");
    } else if (cat.action === "rest" && clock >= cat.until) {
      if (Math.random() < 0.55) walk(clock); else rest(clock);
    }
  }

  function tick(now) {
    if (!running) return;
    var dt = last ? Math.min(0.25, (now - last) / 1000) : 0;
    last = now;
    update(dt);
    draw();
    requestAnimationFrame(tick);
  }

  function setRunning() {
    var should = visible && !document.hidden && !reduce.matches && !!scene;
    if (should && !running) { running = true; last = 0; requestAnimationFrame(tick); }
    if (!should) { running = false; draw(); }
  }

  function say(text) { status.textContent = text; }

  function describe() {
    canvas.setAttribute("aria-label", words["scene_" + phase].replace("{season}", words["season_" + season]));
  }

  function show(name) {
    return load(name).then(function (next) {
      scene = next;
      if (phase === "night" || Math.abs(cat.x - next.meta.spot[0]) > 40) cat.x = next.meta.spot[0];
      describe();
      draw();
      setRunning();
    });
  }

  function pet() {
    if (!scene) return;
    var m = scene.meta;
    var x = phase === "night" ? m.spot[0] : Math.round(cat.x);
    var top = m.spot[1] - (phase === "night" ? 12 : 22);
    var count = phase === "night" ? 2 : 3;
    for (var i = 0; i < count; i++) {
      hearts.push({ x: x - 7 + i * 6, y: top - (i % 2) * 3, born: clock + i * 0.25, life: 1.6 });
    }
    if (phase === "day") {
      cat.action = "pet"; cat.started = clock; cat.until = clock + 2.6;
      say(words.pet_day);
    } else {
      say(words.pet_night);
    }
    draw();
    if (reduce.matches) {
      draw();
      window.setTimeout(function () {
        hearts = [];
        if (phase === "day") rest(clock, "sit");
        draw();
      }, 1800);
    }
  }

  function press(group, value) {
    root.querySelectorAll("[data-" + group + "]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-" + group) === value));
    });
  }

  root.addEventListener("click", function (event) {
    var button = event.target.closest("button");
    if (!button) return;
    if (button.hasAttribute("data-pet")) { pet(); return; }
    if (button.hasAttribute("data-phase")) {
      phase = button.getAttribute("data-phase");
      press("phase", phase);
      hearts = [];
      if (phase === "day") rest(clock, "sit");
      say(words["now_" + phase]);
    }
    if (button.hasAttribute("data-season")) {
      season = button.getAttribute("data-season");
      press("season", season);
      say(words["season_now"].replace("{season}", words["season_" + season]));
    }
    show(season + "-" + phase);
  });

  canvas.addEventListener("click", function (event) {
    if (!scene) return;
    var box = canvas.getBoundingClientRect();
    var x = (event.clientX - box.left) / box.width * W;
    var y = (event.clientY - box.top) / box.height * H;
    var cx = phase === "night" ? scene.meta.spot[0] : cat.x;
    if (Math.abs(x - cx) < 16 && y > scene.meta.spot[1] - 28 && y < scene.meta.spot[1] + 6) pet();
  });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      setRunning();
    }, { threshold: 0.05 }).observe(canvas);
  }
  document.addEventListener("visibilitychange", setRunning);
  if (reduce.addEventListener) reduce.addEventListener("change", function () { rest(clock, "sit"); cat.x = scene ? scene.meta.spot[0] : 80; setRunning(); });

  press("season", season);
  press("phase", phase);
  rest(0, "sit");
  show(season + "-" + phase).then(function () {
    canvas.hidden = false;
    still.hidden = true;
    controls.hidden = false;
  }).catch(function () { /* keep the still picture */ });
})();
