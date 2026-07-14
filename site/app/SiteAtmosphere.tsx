"use client";

import { useEffect } from "react";

const revealSelector = [
  ".section-heading",
  ".resource-card",
  ".blog-card",
  ".info-card",
  ".depth-card",
  ".process-grid article",
  ".dpa-program-grid article",
  ".dpa-rate-board-heading > *",
  ".dpa-rate-tabs button",
  ".dpa-rate-panel",
  ".faq-item",
  ".home-faq-item",
  ".story-copy > *",
  ".rates-grid > *",
  ".final-cta-inner > *",
].join(",");

export default function SiteAtmosphere() {
  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let pointerFrame = 0;

    const updatePointer = (event: PointerEvent) => {
      if (reduceMotion.matches || event.pointerType === "touch") return;
      if (pointerFrame) window.cancelAnimationFrame(pointerFrame);
      pointerFrame = window.requestAnimationFrame(() => {
        root.style.setProperty("--pointer-x", `${event.clientX}px`);
        root.style.setProperty("--pointer-y", `${event.clientY}px`);
      });
    };

    const updateScroll = () => {
      const available = document.documentElement.scrollHeight - window.innerHeight;
      const progress = available > 0 ? Math.min(1, window.scrollY / available) : 0;
      root.style.setProperty("--page-progress", progress.toFixed(4));
    };

    const nodes = Array.from(document.querySelectorAll<HTMLElement>(revealSelector));
    nodes.forEach((node, index) => {
      node.classList.add("motion-reveal");
      node.style.setProperty("--reveal-delay", `${(index % 5) * 65}ms`);
    });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-revealed");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -7% 0px", threshold: 0.08 },
    );

    nodes.forEach((node) => observer.observe(node));
    body.classList.add("motion-ready");
    updateScroll();

    window.addEventListener("pointermove", updatePointer, { passive: true });
    window.addEventListener("scroll", updateScroll, { passive: true });
    window.addEventListener("resize", updateScroll, { passive: true });

    return () => {
      observer.disconnect();
      body.classList.remove("motion-ready");
      window.removeEventListener("pointermove", updatePointer);
      window.removeEventListener("scroll", updateScroll);
      window.removeEventListener("resize", updateScroll);
      if (pointerFrame) window.cancelAnimationFrame(pointerFrame);
      root.style.removeProperty("--pointer-x");
      root.style.removeProperty("--pointer-y");
      root.style.removeProperty("--page-progress");
    };
  }, []);

  return (
    <div className="site-motion-progress" aria-hidden="true"><i /></div>
  );
}
