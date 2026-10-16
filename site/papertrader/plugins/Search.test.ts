import assert from "node:assert/strict";
import test from "node:test";
import {
  createSearchDocument,
  createSearchIndexLoader,
  normalizeSearchText,
  shouldCloseSearchForActivation,
} from "../search";

test("a rejected lazy search load is cleared and the next request can retry", async () => {
  const expected = createSearchDocument("research", "Research", [], "evidence");
  let attempts = 0;
  const load = createSearchIndexLoader(async () => {
    attempts += 1;
    if (attempts === 1) throw new Error("temporary network failure");
    return Response.json([expected]);
  });

  await assert.rejects(load("/searchIndex.json"), /temporary network failure/);
  assert.deepEqual(await load("/searchIndex.json"), [expected]);
  assert.deepEqual(await load("/searchIndex.json"), [expected]);
  assert.equal(attempts, 2);
});

test("only an unmodified primary result activation closes the search", () => {
  const primary = {
    altKey: false,
    button: 0,
    ctrlKey: false,
    metaKey: false,
    shiftKey: false,
  };

  assert.equal(shouldCloseSearchForActivation(primary), true);
  assert.equal(
    shouldCloseSearchForActivation({ ...primary, ctrlKey: true }),
    false,
  );
  assert.equal(
    shouldCloseSearchForActivation({ ...primary, metaKey: true }),
    false,
  );
  assert.equal(
    shouldCloseSearchForActivation({ ...primary, shiftKey: true }),
    false,
  );
  assert.equal(
    shouldCloseSearchForActivation({ ...primary, button: 1 }),
    false,
  );
});

test("metadata-only documents normalize searchable titles and tags", () => {
  const document = createSearchDocument(
    "cafe",
    "Café Holdings",
    ["Énergie"],
    "",
  );

  assert.equal(document.excerpt, "");
  assert.ok(document.text.includes(normalizeSearchText("CAFÉ")));
  assert.ok(document.text.includes(normalizeSearchText("ÉNERGIE")));
});
