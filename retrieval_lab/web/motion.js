"use strict";
// Lenis was chosen over Locomotive Scroll because this workbench keeps native
// document scrolling. Charts and controls stay in the normal accessible flow.
(() => {
  if (!window.gsap || !window.ScrollTrigger || !window.Lenis) return;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  let lenis = null;
  media.add("(prefers-reduced-motion: no-preference)", () => {
    lenis = new Lenis({
      duration: 0.8,
      smoothWheel: true,
      syncTouch: false,
      prevent: (node) => Boolean(node.closest("dialog, .query-list, .history")),
    });
    lenis.on("scroll", ScrollTrigger.update);
    const tick = (time) => lenis?.raf(time * 1000);
    gsap.ticker.add(tick);
    const intro = gsap.timeline({ defaults: { ease: "power3.out" } });
    intro
      .from(".workbench-label", { y: 8, duration: 0.35 })
      .from(".title-word", { y: 22, stagger: 0.075, duration: 0.65 }, 0)
      .from(
        ".hero-copy > p, .hero-copy > .button",
        { y: 12, stagger: 0.08, duration: 0.55 },
        0.15,
      )
      .from(".hero-evidence", { y: 18, rotation: 0, duration: 0.7 }, 0.1);
    const onResults = () => {
      gsap.from(".rank-map-svg path", {
        strokeDasharray: 250,
        strokeDashoffset: 250,
        duration: 0.65,
        stagger: 0.04,
        ease: "power2.out",
      });
      ScrollTrigger.refresh();
      lenis.resize();
    };
    document.addEventListener("lab:results", onResults);
    const section = gsap.from(".query-heading", {
      y: 14,
      duration: 0.55,
      scrollTrigger: {
        trigger: ".query-heading",
        start: "top 94%",
        once: true,
      },
    });
    const visibility = () => {
      if (document.hidden) lenis?.stop();
      else lenis?.start();
    };
    document.addEventListener("visibilitychange", visibility);
    document.fonts.ready.then(() => ScrollTrigger.refresh());
    return () => {
      intro.revert();
      section.revert();
      document.removeEventListener("lab:results", onResults);
      document.removeEventListener("visibilitychange", visibility);
      gsap.ticker.remove(tick);
      lenis?.destroy();
      lenis = null;
    };
  });
  document.querySelector("#workspace-button").addEventListener("click", () => {
    if (lenis) lenis.scrollTo(0);
    else window.scrollTo({ top: 0, behavior: "instant" });
  });
  window.addEventListener("pagehide", () => media.revert(), { once: true });
})();
