// gibplay.com 404: GitHub Pages paths are case-sensitive, so /bitz/... is sent to
// the right address (/Bitz/...). Everything else stays on the helpful 404 page.
(function () {
  "use strict";
  var path = window.location.pathname;
  var match = /^\/bitz(\/.*)?$/i.exec(path);
  if (match && path.indexOf("/Bitz") !== 0) {
    var rest = (match[1] || "/").toLowerCase();
    var known = { "/": "/Bitz/", "/tr/": "/Bitz/tr/", "/support/": "/Bitz/support/", "/privacy/": "/Bitz/privacy/",
      "/tr": "/Bitz/tr/", "/support": "/Bitz/support/", "/privacy": "/Bitz/privacy/" };
    if (known[rest]) window.location.replace(known[rest] + window.location.hash);
  }
})();
