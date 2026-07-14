"use client";

import { useEffect, useState } from "react";
import type { BlogPost } from "./posts";

export default function LatestBlogPosts({ initialPosts }: { initialPosts: BlogPost[] }) {
  const [posts, setPosts] = useState(initialPosts);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    fetch("/api/blog", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Live archive unavailable");
        return response.json() as Promise<{ posts?: BlogPost[] }>;
      })
      .then((payload) => {
        if (active && payload.posts?.length) setPosts(payload.posts.slice(0, 3));
      })
      .catch(() => undefined);

    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  return (
    <div className="resource-grid">
      {posts.map((resource, index) => (
        <a className="resource-card" href={resource.url} key={resource.url}>
          <span className="resource-number">0{index + 1}</span>
          <p className="card-label">{resource.category} · {resource.date}</p>
          <h3>{resource.title}</h3>
          <p>{resource.description}</p>
          <span className="resource-read">Read the article →</span>
        </a>
      ))}
    </div>
  );
}
