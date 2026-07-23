# Responsive Design Fixes

The code editor was invisible on mobile and on resized laptop windows, and several
pages overflowed horizontally on phones. This document lists what changed and why.

## Root causes that were fixed

1. **Editor collapsed to 0 height below 1080px.** The right pane kept
   `flex: 1 1 0` from the desktop split while the media query set `min-height: 0`.
   In a vertical (column) flex stack that combination resolves to a zero-height
   pane, and `.editor-card { overflow: hidden }` then clipped the editor into
   complete invisibility. The CodeMirror element is absolutely positioned, so it
   contributed no intrinsic height that could have rescued the layout.
2. **Editor buried below the statement.** Even when it had height, the stacked
   layout placed the editor after the full problem statement (~2000px down on a
   phone) with no hint it existed.
3. **Top navigation overflowed the viewport on phones** (5 links + user menu),
   giving every page a horizontal scrollbar.
4. **Wide tables** (submissions, standings, leaderboard, home) stretched the page
   sideways on small screens; the `grid-2` layout let cards grow past the viewport.
5. **`100vh` heights** don't track the real visible viewport in mobile browsers
   with dynamic toolbars (iOS Safari, Android Chrome).

## What changed

### `static/css/style.css`
- New `.mobile-tabs` component: a sticky "Description | Code" segmented control
  shown at ≤1080px (LeetCode-mobile style).
- Rewrote the `@media (max-width: 1080px)` problem-page block:
  - panes get `flex: none` so they can never flex-collapse;
  - the editor keeps a guaranteed height (`clamp(280px, 45vh/45dvh, 540px)`)
    in the no-JS stacked fallback;
  - with JS tabs active, the Code view sizes the pane to the visible viewport
    (`calc(100dvh - measured chrome)`) so editor, console toggle, Run and
    Submit all fit on one screen.
- `@supports (height: 100dvh)` overrides so heights track the real mobile
  viewport (desktop split panes, mobile editor, chat box).
- Topbar now wraps at ≤920px (it needs ~900px for one row): brand + user on the
  first row, links become one swipeable row (`overflow-x: auto`, hidden
  scrollbar) that can never widen the page.
- `.table-scroll` utility: wide tables scroll sideways inside their card instead
  of stretching the page; `.grid-2 > * { min-width: 0 }` lets grid cells shrink.
- Touch/mobile polish: 16px form fields (stops iOS focus auto-zoom), 44px
  minimum touch targets for primary buttons, larger copy-button hit areas,
  keyboard-hint and console-explainer text hidden on phones, tighter card
  padding and headings on small screens, `-webkit-text-size-adjust: 100%`.

### `templates/judge/problem_detail.html`
- Added the tab bar markup (plain `#statement-pane` / `#submit` anchor links —
  they still work as jump links if JavaScript is off; JS upgrades them to tabs).
- Added the tabs script: switches views, remembers the chosen tab per problem
  (sessionStorage), measures the real chrome height into `--code-top`,
  re-measures on resize/orientation change, and calls `editor.refresh()`
  whenever the CodeMirror becomes visible so it never renders blank.
- Desktop (>1080px) is untouched: same split view, draggable divider, saved
  split ratio.

### Table templates
Wrapped every `<table>` in `<div class="table-scroll">` in: `home.html`,
`accounts/profile.html`, `judge/problem_list.html`, `judge/contest_detail.html`,
`judge/submission_list.html`, `judge/leaderboard.html`,
`judge/submission_detail.html`, `judge/contest_list.html`,
`judge/standings.html`.

## Verified

Automated checks (headless Chromium) at 320–1440px widths, logged in and out:
- 0px horizontal overflow on home, problems, submissions, problem page, login
  at 15 widths (320, 360, 375, 414, 600, 700, 768, 820, 860, 900, 940, 1024,
  1080, 1100, 1280);
- Code tab: editor visible, ≥280px tall, accepts typing, console toggles,
  Submit button fully on screen — at 375, 414, 768, 1024;
- no-JS fallback keeps a ≥280px editor; logged-out Code tab shows the login card;
- desktop split view unchanged at 1100/1280/1440.
