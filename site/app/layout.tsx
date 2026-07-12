import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

const origin = "https://drmortgageusa.com";
const indexable = process.env.NEXT_PUBLIC_INDEXABLE === "true";

export const metadata: Metadata = {
    metadataBase: new URL(origin),
    title: {
      default: "DR. Mortgage USA | Florida Mortgage Guidance",
      template: "%s | DR. Mortgage USA",
    },
    description:
      "Clear mortgage options, useful calculators, and human guidance for Florida buyers and homeowners.",
    icons: {
      icon: "/media/logo.webp",
      shortcut: "/media/logo.webp",
      apple: "/media/logo.webp",
    },
    openGraph: {
      title: "DR. Mortgage USA",
      description: "Understand the numbers before you make the move.",
      type: "website",
      images: [{ url: `${origin}/og.png`, width: 1200, height: 675, alt: "DR. Mortgage USA: Understand the numbers before you make the move." }],
    },
    twitter: {
      card: "summary_large_image",
      title: "DR. Mortgage USA",
      description: "Understand the numbers before you make the move.",
      images: [`${origin}/og.png`],
    },
    robots: { index: indexable, follow: indexable },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head />
      <body>
        <Script src="/site-tracking.js" strategy="beforeInteractive" />
        {children}
      </body>
    </html>
  );
}
