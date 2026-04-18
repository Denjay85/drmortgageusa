declare global {
  interface Window {
    fbq?: (...args: unknown[]) => void;
  }
}

const META_PIXEL_ID = import.meta.env.VITE_META_PIXEL_ID || "444762220810129";

let pixelInitialized = false;

function getCookie(name: string) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(";").shift() || "";
  }
  return "";
}

function setCookie(name: string, value: string, days: number) {
  const expires = new Date(Date.now() + days * 86400000).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
}

function ensureFbpCookie() {
  let fbp = getCookie("_fbp");
  if (!fbp) {
    fbp = `fb.1.${Date.now()}.${Math.floor(Math.random() * 1000000000)}`;
    setCookie("_fbp", fbp, 90);
  }
  return fbp;
}

function ensureFbcCookie() {
  let fbc = getCookie("_fbc");
  const params = new URLSearchParams(window.location.search);
  const fbclid = params.get("fbclid");

  if (fbclid) {
    fbc = `fb.1.${Date.now()}.${fbclid}`;
    setCookie("_fbc", fbc, 90);
  }

  return fbc || "";
}

function getRouteName(path: string) {
  if (path === "/") return "home";
  return path.replace(/^\//, "").replace(/\//g, "_") || "home";
}

export function initMetaPixel() {
  if (pixelInitialized || !META_PIXEL_ID || typeof window === "undefined") {
    return;
  }

  if (typeof window.fbq !== "function") {
    ((f: Window & typeof globalThis, b: Document, e: string, v: string) => {
      const maybeFbq = f.fbq as
        | (((...args: unknown[]) => void) & {
            callMethod?: (...args: unknown[]) => void;
            queue?: unknown[];
            loaded?: boolean;
            version?: string;
          })
        | undefined;

      if (maybeFbq) return;

      const n = function (...args: unknown[]) {
        if (n.callMethod) {
          n.callMethod(...args);
        } else {
          n.queue?.push(args);
        }
      } as typeof maybeFbq;

      if (!f._fbq) {
        f._fbq = n;
      }
      n.push = n;
      n.loaded = true;
      n.version = "2.0";
      n.queue = [];

      const t = b.createElement(e);
      t.async = true;
      t.src = v;
      const s = b.getElementsByTagName(e)[0];
      s.parentNode?.insertBefore(t, s);
      f.fbq = n;
    })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
  }

  ensureFbpCookie();
  ensureFbcCookie();
  window.fbq?.("init", META_PIXEL_ID);
  pixelInitialized = true;
}

export function trackPageView(path: string) {
  if (!pixelInitialized) return;
  window.fbq?.("track", "PageView", {
    content_name: getRouteName(path),
    content_category: "refiwatch",
  });
}

export function trackViewContent(path: string) {
  if (!pixelInitialized) return;
  window.fbq?.("track", "ViewContent", {
    content_name: getRouteName(path),
    content_category: "refiwatch",
  });
}

export function trackLead({
  eventId,
  contentName,
  currentRate,
}: {
  eventId?: string;
  contentName: string;
  currentRate?: string;
}) {
  if (!pixelInitialized) return;
  window.fbq?.(
    "track",
    "Lead",
    {
      content_name: contentName,
      content_category: "refiwatch",
      current_rate: currentRate || "",
    },
    eventId ? { eventID: eventId } : undefined,
  );
}

export function trackContact(contentName: string) {
  if (!pixelInitialized) return;
  window.fbq?.("track", "Contact", {
    content_name: contentName,
    content_category: "refiwatch",
  });
}
