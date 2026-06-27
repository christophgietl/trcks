# AI coding agent instructions for `docs/` and its subdirectories

## Prefer `mkdocs-material` admonitions over regular highlighting

Do not use:

```markdown
**See also:** Scott Wlaschin's blog post
[Railway oriented programming](https://fsharpforfunandprofit.com/posts/recipe-part2/)
comes with lots of examples.
```

Use:

```markdown
???+ tip "See also"
    Scott Wlaschin's blog post
    [Railway oriented programming](https://fsharpforfunandprofit.com/posts/recipe-part2/)
    comes with lots of examples.
```
