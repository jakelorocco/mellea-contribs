// SPA tab routing for the mellea-contribs docs site.
// Hash format: "#/" -> overview, "#/<package-name>" -> package detail.
(function () {
  "use strict";

  var panes = document.querySelectorAll(".pane");
  var links = document.querySelectorAll(".pkg-link");

  function targetForHash(hash) {
    if (!hash || hash === "#" || hash === "#/" || hash === "#/overview") {
      return "overview";
    }
    if (hash.indexOf("#/") === 0) {
      return "pkg-" + hash.slice(2);
    }
    // Fall through: in-page anchor (e.g. #version-history). Don't switch panes.
    return null;
  }

  function show(target) {
    if (!target) return;
    var found = false;
    for (var i = 0; i < panes.length; i++) {
      if (panes[i].id === target) {
        panes[i].hidden = false;
        found = true;
      } else {
        panes[i].hidden = true;
      }
    }
    if (!found) {
      // Unknown hash: fall back to overview rather than showing nothing.
      var overview = document.getElementById("overview");
      if (overview) overview.hidden = false;
      target = "overview";
    }
    for (var j = 0; j < links.length; j++) {
      var active = links[j].getAttribute("data-target") === target;
      links[j].classList.toggle("active", active);
      links[j].setAttribute("aria-selected", active ? "true" : "false");
    }
    // Reset scroll so package navigation feels like a page change.
    if (typeof window.scrollTo === "function") {
      window.scrollTo(0, 0);
    }
  }

  function onHashChange() {
    var t = targetForHash(window.location.hash);
    if (t !== null) show(t);
  }

  // Intercept clicks on internal pkg-link anchors so we don't double-handle.
  for (var k = 0; k < links.length; k++) {
    links[k].addEventListener("click", function (e) {
      var target = this.getAttribute("data-target");
      // Let the browser update the hash; the hashchange listener does the work.
      // No preventDefault — we want history entries.
      // But if we're already on the same target, scroll to top manually.
      if (window.location.hash === this.getAttribute("href")) {
        e.preventDefault();
        show(target);
      }
    });
  }

  window.addEventListener("hashchange", onHashChange);
  onHashChange();
})();
