(function () {
  var meta = document.querySelector('meta[name="meowoo-admin-origin"]');
  if (!meta || !meta.content) return;

  var adminOrigin = meta.content.replace(/\/$/, "");

  fetch(adminOrigin + "/auth/status", {
    credentials: "include",
    mode: "cors",
  })
    .then(function (res) {
      if (!res.ok) return null;
      return res.json();
    })
    .then(function (data) {
      if (!data || !data.authenticated) return;

      var sections = data.sections || [];
      var path = window.location.pathname || "";
      var postMatch = path.match(/\/(ramble|looksie|nom|stomp)\/([^/]+)\.html$/);

      var bar = document.createElement("nav");
      bar.className = "author-toolbar";
      bar.setAttribute("aria-label", "Author tools");

      function link(href, label) {
        var a = document.createElement("a");
        a.href = href;
        a.textContent = label;
        return a;
      }

      bar.appendChild(link(adminOrigin + "/admin", "Dashboard"));
      bar.appendChild(link(adminOrigin + "/admin/new", "New post"));

      if (postMatch) {
        var section = postMatch[1];
        var slug = postMatch[2];
        if (sections.indexOf(section) !== -1) {
          bar.appendChild(
            link(
              adminOrigin + "/admin/edit/" + section + "/" + slug,
              "Edit this post"
            )
          );
        }
      }

      bar.appendChild(link(adminOrigin + "/login", "Account"));
      document.body.appendChild(bar);
    })
    .catch(function () {
      /* not logged in or CORS / network */
    });
})();
