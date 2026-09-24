# AI coding agent instructions for `docs/` and its subdirectories

## Documentation structure

- Sort entries alphabetically by term in [the glossary](glossary.md).
- Keep usage docs split by style in `docs/usage/oop/` and `docs/usage/fp/`.
- Within each style, keep the `index.md`, `sync.md`, `async.md`, and
  `tuples.md` structure.
- Keep the two styles structurally symmetric.
- Keep the overview matrices in the `index.md` pages up to date.

## Prefer `mkdocs-material` admonitions over regular highlighting

Do not write:

```markdown
**See also:** Scott Wlaschin's blog post
[Railway oriented programming](https://fsharpforfunandprofit.com/posts/recipe-part2/)
comes with lots of examples.
```

Write instead:

```markdown
???+ tip "See also"
    Scott Wlaschin's blog post
    [Railway oriented programming](https://fsharpforfunandprofit.com/posts/recipe-part2/)
    comes with lots of examples.
```

## Keep cross-references out of headings

Write headings with plain code spans (e.g. `## Single-track code with \`trcks.oop.Wrapper\``).
Do not use cross-references (e.g. `` [`Wrapper`][trcks.oop.Wrapper] ``) inside headings.
rumdl and mkdocs compute different slug anchors for headings that contain
cross-references, so such headings cannot satisfy both tools at once.

## Further instructions

- Use expanded admonitions (`???+ example`) for primary examples.
- Use collapsed admonitions (`??? example "Step by step"`) for optional
  step-by-step breakdowns and other optional deep-dives.
- Keep doctest examples self-contained per file.
  Each file must define all imports and helper functions that it uses.
- Keep prose lines at most 80 characters long (rule MD013).
