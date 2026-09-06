#!/usr/bin/env node
// Stop hook: the deterministic half of the clear-writing rules.
//
// An instruction in CLAUDE.md is context, and context loses to a long session. This checks the
// text actually about to be sent and blocks it, so the mechanical rules hold whatever else is
// going on. It only enforces what a regex can decide: em dashes, banned phrases, banned words.
// Judgment (structure, filler, whether a sentence earns its place) stays with the model.
//
// Fails OPEN on every internal error. A style check must never be able to brick a session.

import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const CONFIG = join(homedir(), ".claude", "hooks", "clear-writing-rules.json");

const DEFAULTS = {
  // Em dash, and en dash used as a sentence break (spaced). Hyphens are untouched.
  patterns: [
    { id: "em-dash", re: "\\u2014", say: "em dash. Use a comma, colon, period, or parentheses." },
    { id: "en-dash-break", re: "\\s\\u2013\\s", say: "en dash as a sentence break. Use a comma, colon, or period." }
  ],
  phrases: [
    "great question", "let's dive in", "i'd be happy to", "in today's fast-paced",
    "let me know if you have any questions", "hope this helps", "feel free to",
    "it's worth noting", "at its core", "in essence", "that's the real win",
    "let me explain", "as mentioned earlier", "please note", "note that,"
  ],
  words: [
    "delve", "seamless", "seamlessly", "robust", "crucial", "comprehensive",
    "landscape", "journey", "elevate", "streamline", "empower", "unlock",
    "supercharge", "game-changer", "importantly", "notably"
  ],
  // Words that are legitimate in a technical sentence often enough to warn rather than block.
  warnOnly: ["comprehensive", "robust"]
};

function loadRules() {
  try {
    return { ...DEFAULTS, ...JSON.parse(readFileSync(CONFIG, "utf8")) };
  } catch {
    return DEFAULTS;
  }
}

/** Strip anything that is not prose the reader judges: code, quotes, links, tool output. */
function proseOnly(text) {
  return text
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/~~~[\s\S]*?~~~/g, " ")
    .replace(/`[^`\n]*`/g, " ")
    .replace(/^\s*>.*$/gm, " ")
    .replace(/\]\([^)]*\)/g, "]")
    .replace(/https?:\/\/\S+/g, " ");
}

function lastAssistantText(transcriptPath) {
  const lines = readFileSync(transcriptPath, "utf8").split("\n").filter(Boolean);
  for (let i = lines.length - 1; i >= 0; i -= 1) {
    let entry;
    try {
      entry = JSON.parse(lines[i]);
    } catch {
      continue;
    }
    if (entry?.type !== "assistant") continue;
    const content = entry.message?.content;
    if (!Array.isArray(content)) continue;
    const text = content.filter((part) => part?.type === "text").map((part) => part.text).join("\n").trim();
    if (text) return text;
  }
  return "";
}

function findings(text, rules) {
  const prose = proseOnly(text);
  const lower = prose.toLowerCase();
  const hits = [];

  for (const pattern of rules.patterns) {
    if (new RegExp(pattern.re, "u").test(prose)) hits.push({ blocking: true, say: pattern.say });
  }
  for (const phrase of rules.phrases) {
    if (lower.includes(phrase)) hits.push({ blocking: true, say: `banned phrase "${phrase}"` });
  }
  for (const word of rules.words) {
    if (new RegExp(`\\b${word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(lower)) {
      hits.push({ blocking: !rules.warnOnly.includes(word), say: `slop word "${word}"` });
    }
  }
  return hits;
}

function main() {
  let input = "";
  try {
    input = readFileSync(0, "utf8");
  } catch {
    process.exit(0);
  }

  let payload;
  try {
    payload = JSON.parse(input);
  } catch {
    process.exit(0);
  }

  // Already blocked once this turn. Blocking again would loop forever.
  if (payload.stop_hook_active) process.exit(0);
  if (!payload.transcript_path) process.exit(0);

  let text = "";
  try {
    text = lastAssistantText(payload.transcript_path);
  } catch {
    process.exit(0);
  }
  if (!text) process.exit(0);

  const rules = loadRules();
  const hits = findings(text, rules);
  const blocking = hits.filter((hit) => hit.blocking);
  if (blocking.length === 0) process.exit(0);

  const reason = [
    "Your reply breaks the clear-writing rules that apply to every human-facing output:",
    ...blocking.slice(0, 8).map((hit) => `- ${hit.say}`),
    "",
    "Rewrite the reply without them and send that instead. Do not explain the correction."
  ].join("\n");

  process.stdout.write(JSON.stringify({ decision: "block", reason }));
  process.exit(0);
}

main();
