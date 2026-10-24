/* Site header: the compact menu and the globe language menu.
   Loaded in <head> without defer, so the "js" class is set before the first paint
   and the menus never flash open. Without JavaScript every link stays visible.
   No storage, no cookies: choosing a language is just following a link. */
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");

  function init() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    var nav = document.getElementById("site-nav");
    var navBtn = header.querySelector(".menu-btn");
    var langMenu = header.querySelector(".lang-menu");
    var langBtn = langMenu && langMenu.querySelector(".lang-btn");
    var langLinks = langMenu ? Array.prototype.slice.call(langMenu.querySelectorAll("a[data-lang]")) : [];
    var bilingual = langMenu && langMenu.hasAttribute("data-bilingual");
    var compact = window.matchMedia("(max-width: 44.99em)");

    // Anchor targets stay clear of the sticky header, whatever its height.
    function syncHeight() { root.style.setProperty("--header-h", header.offsetHeight + "px"); }
    syncHeight();
    if ("ResizeObserver" in window) new ResizeObserver(syncHeight).observe(header);

    function setNav(open, focusFirst) {
      if (!navBtn) return;
      navBtn.setAttribute("aria-expanded", String(open));
      header.classList.toggle("nav-open", open);
      if (open) {
        setLang(false);
        if (focusFirst) { var first = nav.querySelector("a"); if (first) first.focus(); }
      }
    }

    // scroll-padding leaves 16px under the header, so a just-followed anchor still counts.
    function headerOffset() { return header.getBoundingClientRect().bottom + 32; }

    // The section the visitor is reading: the last one whose top has passed under the header.
    function currentSection() {
      var found = null;
      var limit = headerOffset();
      var nodes = document.querySelectorAll("main section[id], main h2[id], main h3[id]");
      for (var i = 0; i < nodes.length; i++) {
        var id = nodes[i].id;
        if (/-(heading|title)$/.test(id)) continue;
        if (nodes[i].getBoundingClientRect().top <= limit) found = id; else break;
      }
      return found;
    }

    function refreshLang() {
      var section = currentSection();
      // Bilingual pages (support, privacy): English sections are "x", the Turkish half is "tr" and "tr-x".
      var active = bilingual ? (section && /^tr(-|$)/.test(section) ? "tr" : "en") : root.lang;
      langLinks.forEach(function (link) {
        var code = link.getAttribute("data-lang");
        if (code === active) link.setAttribute("aria-current", "true"); else link.removeAttribute("aria-current");
        if (!link.hasAttribute("data-base")) link.setAttribute("data-base", link.getAttribute("href"));
        var base = link.getAttribute("data-base");
        var href = base;
        if (bilingual) {
          if (section) {
            var plain = section.replace(/^tr-/, "");
            var target = code === "tr" ? (section === "tr" ? "tr" : "tr-" + plain) : (section === "tr" ? "main" : plain);
            if (document.getElementById(target)) href = "#" + target;
          }
        } else if (section) {
          href = base + "#" + section;  // the localized pages share their section IDs
        }
        link.setAttribute("href", href);
      });
      if (langBtn) langBtn.setAttribute("aria-label", langBtn.getAttribute("data-label-" + active) || langBtn.getAttribute("aria-label"));
    }

    function setLang(open, focusItem) {
      if (!langBtn) return;
      if (open) { setNav(false); refreshLang(); }
      langBtn.setAttribute("aria-expanded", String(open));
      langMenu.classList.toggle("open", open);
      if (open && focusItem) {
        var current = langMenu.querySelector('a[aria-current="true"]') || langLinks[0];
        if (current) current.focus();
      }
    }

    if (navBtn && nav) {
      navBtn.addEventListener("click", function (e) {
        // A keyboard press arrives as a click with detail 0: move focus into the menu then.
        setNav(navBtn.getAttribute("aria-expanded") !== "true", e.detail === 0);
      });
      nav.addEventListener("click", function (e) {
        if (e.target.closest("a")) setNav(false);
      });
      var onChange = function () { if (!compact.matches) setNav(false); };
      if (compact.addEventListener) compact.addEventListener("change", onChange); else compact.addListener(onChange);
    }

    if (langBtn) {
      langBtn.addEventListener("click", function (e) {
        setLang(langBtn.getAttribute("aria-expanded") !== "true", e.detail === 0);
      });
      langBtn.addEventListener("focus", refreshLang);
      if (bilingual) {
        // One page holds both languages, so the globe's label follows the part being read.
        var queued = false;
        window.addEventListener("scroll", function () {
          if (queued) return;
          queued = true;
          window.requestAnimationFrame(function () { queued = false; refreshLang(); });
        }, { passive: true });
        refreshLang();
      }
      langBtn.addEventListener("pointerenter", refreshLang);
      langMenu.addEventListener("keydown", function (e) {
        var i = langLinks.indexOf(document.activeElement);
        var next = null;
        if (e.key === "ArrowDown") next = langLinks[(i + 1) % langLinks.length];
        else if (e.key === "ArrowUp") next = langLinks[(i - 1 + langLinks.length) % langLinks.length];
        else if (e.key === "Home") next = langLinks[0];
        else if (e.key === "End") next = langLinks[langLinks.length - 1];
        if (next && langMenu.classList.contains("open")) { e.preventDefault(); next.focus(); }
      });
      langLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
          refreshLang();
          if (link.getAttribute("aria-current") === "true" && !bilingual) {
            e.preventDefault();  // already in this language
            setLang(false);
            langBtn.focus();
            return;
          }
          setLang(false);
        });
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      if (langMenu && langMenu.classList.contains("open")) { setLang(false); langBtn.focus(); }
      else if (header.classList.contains("nav-open")) { setNav(false); navBtn.focus(); }
    });

    document.addEventListener("click", function (e) {
      if (langMenu && !langMenu.contains(e.target)) setLang(false);
      if (navBtn && !nav.contains(e.target) && !navBtn.contains(e.target)) setNav(false);
    });

    // Close a menu once keyboard focus has left it.
    header.addEventListener("focusout", function (e) {
      var to = e.relatedTarget;
      if (!to) return;
      if (langMenu && !langMenu.contains(to)) setLang(false);
      if (navBtn && !nav.contains(to) && to !== navBtn) setNav(false);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
