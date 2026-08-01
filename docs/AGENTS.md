# AI coding agent instructions for `docs/` and its subdirectories

## Documentation structure

- Sort entries alphabetically by term in [the glossary](glossary.md).
- Keep usage docs split by style in `docs/usage/oop/` and `docs/usage/fp/`.
- Within each style, keep the `index.md`, `sync.md`, `async.md`, and
  `tuples.md` structure.
- Keep the two styles structurally symmetric, and keep the overview matrices
  in the `index.md` pages up to date.

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

## Further instructions

- Use expanded admonitions (`???+ example`) for primary examples.
- Use collapsed admonitions (`??? example "Step by step"`) for optional
  step-by-step breakdowns and other optional deep-dives.
- Keep doctest examples self-contained per file. Every Markdown file is
  doctested independently, so each file must define all imports and helper
  functions that it uses.
