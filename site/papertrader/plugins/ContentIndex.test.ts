import assert from "node:assert/strict";
import test from "node:test";
import type { Root } from "hast";
import { extractSearchText } from "./ContentIndex";

test("search prose excludes large echart payloads without dropping surrounding text", () => {
  const numericPayload = "1234567890,".repeat(100_000);
  const tree: Root = {
    type: "root",
    children: [
      {
        type: "element",
        tagName: "p",
        properties: {},
        children: [{ type: "text", value: "Thesis before chart" }],
      },
      {
        type: "element",
        tagName: "figure",
        properties: { dataRehypePrettyCodeFigure: "" },
        children: [
          {
            type: "element",
            tagName: "pre",
            properties: { dataLanguage: "echart" },
            children: [{ type: "text", value: numericPayload }],
          },
        ],
      },
      {
        type: "element",
        tagName: "p",
        properties: {},
        children: [{ type: "text", value: "Catalyst after chart" }],
      },
    ],
  };

  const text = extractSearchText(tree);
  assert.equal(text, "Thesis before chart Catalyst after chart");
  assert.ok(text.length < numericPayload.length / 1_000);
});
