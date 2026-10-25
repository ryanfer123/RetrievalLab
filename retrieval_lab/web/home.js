"use strict";

(() => {
  const select = document.getElementById("home-query");
  const rankings = document.getElementById("preview-rankings");
  const escapeHtml = (value) =>
    String(value).replace(
      /[&<>"']/g,
      (character) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[character],
    );
  let example = null;
  const render = (index) => {
    const query = example.results.queries[index];
    rankings.innerHTML = ["bm25", "tfidf"]
      .map(
        (method) =>
          `<section class="preview-method ${method}"><div class="preview-method-heading"><span class="dot"></span>${method === "bm25" ? "BM25" : "TF-IDF cosine"}</div><ol class="preview-ranking">${query.results[method].ranking.map((item) => `<li><div class="preview-result-title">${escapeHtml(item.id)}${query.relevant_ids.includes(item.id) ? '<span class="relevant">Relevant</span>' : ""}</div><p>${escapeHtml(item.text.slice(0, 85))}${item.text.length > 85 ? "…" : ""}</p><span class="preview-score">Raw score ${item.score.toFixed(4)}</span></li>`).join("")}</ol></section>`,
      )
      .join("");
    document.dispatchEvent(new CustomEvent("lab:preview"));
  };
  select?.addEventListener("change", () => {
    if (example) render(Number(select.value));
  });
  fetch("/home-demo.json")
    .then((response) => {
      if (!response.ok) throw new Error("Demo unavailable");
      return response.json();
    })
    .then((data) => {
      example = data;
      select.innerHTML = example.results.queries
        .map(
          (query, index) =>
            `<option value="${index}">${escapeHtml(query.text)}</option>`,
        )
        .join("");
      select.value = "1";
      select.disabled = false;
      render(1);
    })
    .catch(() => {
      const message = document.createElement("p");
      message.className = "preview-error";
      message.textContent =
        "The interactive demo could not load. The fixed preview remains visible; open the workbench to run a comparison.";
      document.querySelector(".preview").append(message);
    });

  document.querySelectorAll(".mobile-menu nav a").forEach((link) =>
    link.addEventListener("click", () => {
      document.querySelector(".mobile-menu").open = false;
    }),
  );
  if (!window.gsap || !window.ScrollTrigger || !window.Lenis) return;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  media.add("(prefers-reduced-motion: no-preference)", () => {
    const lenis = new Lenis({
      duration: 0.8,
      smoothWheel: true,
      syncTouch: false,
      anchors: true,
      prevent: (node) =>
        Boolean(node.closest("select,input,summary,.mobile-menu,pre")),
    });
    const tick = (time) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    lenis.on("scroll", ScrollTrigger.update);
    const intro = gsap.timeline({ defaults: { ease: "power3.out" } });
    intro
      .from(".hero-word", { y: 22, duration: 0.65, stagger: 0.06 }, 0)
      .from(
        ".hero-description,.hero-actions",
        { y: 12, duration: 0.55, stagger: 0.08 },
        0.12,
      )
      .from(".preview", { y: 18, rotation: 0, duration: 0.7 }, 0.1);
    const reveals = Array.from(
      document.querySelectorAll(".reveal-heading"),
    ).map((heading) => {
      const original = Array.from(heading.childNodes);
      const label = heading.getAttribute("aria-label");
      heading.setAttribute(
        "aria-label",
        original
          .map((node) => (node.nodeName === "BR" ? " " : node.textContent))
          .join("")
          .replace(/\s+/g, " ")
          .trim(),
      );
      const fragment = document.createDocumentFragment();
      original.forEach((node) => {
        if (node.nodeType !== Node.TEXT_NODE) {
          fragment.append(node.cloneNode(true));
          return;
        }
        node.textContent.split(/(\s+)/).forEach((part) => {
          if (!part.trim()) {
            fragment.append(document.createTextNode(part));
            return;
          }
          const word = document.createElement("span");
          word.className = "heading-word";
          word.setAttribute("aria-hidden", "true");
          word.textContent = part;
          fragment.append(word);
        });
      });
      heading.replaceChildren(fragment);
      const tween = gsap.from(heading.querySelectorAll(".heading-word"), {
        y: 15,
        duration: 0.55,
        stagger: 0.035,
        ease: "power2.out",
        scrollTrigger: { trigger: heading, start: "top 94%", once: true },
      });
      return {
        revert() {
          tween.revert();
          heading.replaceChildren(...original);
          if (label === null) heading.removeAttribute("aria-label");
          else heading.setAttribute("aria-label", label);
        },
      };
    });
    let active = true;
    const refresh = () => {
      if (!active) return;
      lenis.resize();
      ScrollTrigger.refresh();
    };
    document.fonts.ready.then(refresh);
    document.addEventListener("lab:preview", refresh);
    const disclosures = document.querySelectorAll("details");
    disclosures.forEach((details) =>
      details.addEventListener("toggle", refresh),
    );
    const image = document.querySelector(".workspace-preview img");
    image?.addEventListener("load", refresh);
    const visibility = () => (document.hidden ? lenis.stop() : lenis.start());
    document.addEventListener("visibilitychange", visibility);
    return () => {
      active = false;
      intro.revert();
      reveals.forEach((reveal) => reveal.revert());
      gsap.ticker.remove(tick);
      lenis.destroy();
      document.removeEventListener("lab:preview", refresh);
      disclosures.forEach((details) =>
        details.removeEventListener("toggle", refresh),
      );
      image?.removeEventListener("load", refresh);
      document.removeEventListener("visibilitychange", visibility);
    };
  });
  window.addEventListener("pagehide", () => media.revert(), { once: true });
})();
