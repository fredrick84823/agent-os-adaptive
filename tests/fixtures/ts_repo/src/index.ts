import { a } from "./a";
import type { T } from "./types";
import x from "@/util/x";
import React from "react";
import { readFileSync } from "node:fs";
import styles from "./s.css";
import { shared } from "@fx/shared";
import ghost from "@ghost/thing";
import missing from "./nope";
export * from "./lib";

export async function main(name: string): Promise<T> {
  const lazy = await import("./lazy");
  const plugin = await import(`./plugins/${name}`);
  return { a, x, React, readFileSync, styles, shared, ghost, missing, lazy, plugin } as unknown as T;
}
