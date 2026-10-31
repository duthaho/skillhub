# Archetypes

A slide is one archetype (sometimes two stacked: e.g. `code` over an
`ask`). Each entry: **when** to use it, the **markup** (classes from
`assets/deck.css`), and the **steps** that make it teach. Skeletons are
minimal — fill them with fact-sheet data, never lorem.

Every slide file wraps its archetype in the template's
`<section class="slide">` → `.slide-head` → `.slide-body` → optional
`.slide-foot` → `.notes`.

---

## cover — title card
**When:** slide 1 of a series episode, or the thumbnail frame.
```html
<section class="slide cover" data-slug="cover">
  <span class="badge info enter">SYSTEM DESIGN · TẬP 07</span>
  <h1 class="title cover-title enter" style="--d:120ms">Phân trang 2 triệu đơn: OFFSET, keyset, hay index?</h1>
  <p class="cover-sub enter" style="--d:240ms">Một màn admin, ba lần đổi ý — và cái thật sự làm chậm nằm ở chỗ khác.</p>
  <div class="cover-meta enter" style="--d:360ms"><span class="tag">MySQL 8</span><span class="tag">~12 phút</span></div>
</section>
```
**Steps:** none — `.enter` with staggered `--d` plays the reveal on arrival.
The cobalt edge bar and the title block come from the CSS/engine.

## split — compare two states
**When:** before/after, naive/better, A/B, "what you think / what happens".
The workhorse; most decks use it 3–5 times.
```html
<div class="slide-body cols-2">
  <div class="card">
    <span class="badge">BÂY GIỜ</span>
    <div class="card-head">Phân trang OFFSET</div>
    <div class="code">…</div>
    <!-- a visual of the cost: scan track, table, stat -->
  </div>
  <div class="card a-right" data-step="2">
    <span class="badge info">ĐỀ XUẤT</span>
    <div class="card-head">Keyset (seek)</div>
    …
  </div>
</div>
<footer class="slide-foot">
  <div class="callout problem a-pop" data-step="3"><div class="callout-title">Trang càng sâu càng chậm</div><p>…</p></div>
  <div class="callout fix a-pop" data-step="3" style="--d:150ms"><div class="callout-title">Trang 40.000 nhanh ngang trang 1</div><p>…</p></div>
</footer>
```
**Steps:** left cost → right alternative → both bottom lines.

## trace — a request through a topology
**When:** any architecture: client → LB → service → cache → DB; CDN; queue
workers; auth flow. Shows *one* real request, hop by hop.
```html
<div class="diagram" style="width:1728px;height:560px">
  <svg class="wires" viewBox="0 0 1728 560">
    <path class="wire a-draw" data-step="1" pathLength="1" d="M290 280 H520" marker-end="url(#ad-arrow)"/>
    <text class="wire-label" x="405" y="262" text-anchor="middle">GET /orders?after=…</text>
    <path class="wire a-draw" data-step="2" pathLength="1" d="M770 280 H1000" marker-end="url(#ad-arrow)"/>
    <path class="wire dashed muted" d="M895 330 V440 H1000"/>
  </svg>
  <div class="node" style="--x:40px;--y:228px"><div class="node-type">Client</div><div class="node-title">CS admin</div></div>
  <div class="node a-info" data-step="1" style="--x:520px;--y:228px"><div class="node-type">API</div><div class="node-title">orders-svc</div><div class="node-meta">p99 40 ms</div></div>
  <div class="node" style="--x:1000px;--y:228px"><div class="node-type">MySQL 8</div><div class="node-title">orders</div><div class="node-meta">2M rows / shop</div></div>
  <div class="packet a-packet" data-step="1" style="--d:500ms;offset-path:path('M290 280 H520')"></div>
  <div class="packet a-packet" data-step="2" style="--d:500ms;offset-path:path('M770 280 H1000')"></div>
  <span class="pin problem" data-step="3" style="--x:1010px;--y:190px">full scan</span>
</div>
```
Coordinates: `.diagram` is W×H px, the svg `viewBox` is `0 0 W H`, nodes
use `--x/--y` (top-left) in the same px. Node ≈ 250×100 by default
(`--w` to change). Wires go edge-to-edge between nodes. Packets use the
same path string as their wire. Up to ~7 nodes; more → split the slide or
group into a `.node.ghost` boundary.
**Steps:** one hop per step (wire draws, packet travels, target node
lights). Last step: the verdict pin or a `stat` for total latency.

## sequence — who talks to whom, in order
**When:** protocols and handshakes: OAuth, TLS, 2PC, saga, cache-aside,
retries with idempotency keys, websockets upgrade.
```html
<div class="seq" style="--n:4">
  <div class="seq-head">
    <div class="seq-actor">Client</div><div class="seq-actor">API</div>
    <div class="seq-actor">Redis<small>cache</small></div><div class="seq-actor">DB</div>
  </div>
  <div class="seq-msg" data-step="1" style="--a:1;--b:2"><span>GET /product/42</span></div>
  <div class="seq-msg problem" data-step="2" style="--a:2;--b:3"><span>GET p:42 → miss</span></div>
  <div class="seq-msg" data-step="3" style="--a:2;--b:4"><span>SELECT … WHERE id=42</span></div>
  <div class="seq-msg back dashed" data-step="4" style="--a:2;--b:4"><span>row (38 ms)</span></div>
  <div class="seq-note" data-step="5" style="--a:3;--b:3"><span>SET p:42 EX 300</span></div>
  <div class="seq-sep" data-step="6"><span>… 1.000 request cùng lúc khi key hết hạn …</span></div>
</div>
```
`--a` < `--b` always (left actor, right actor); `.back` points the arrow
left. ≤ 8 messages per slide; continue on the next slide.
**Steps:** one message per step; the surprising one gets a tone + a note.

## lanes — concurrency and time
**When:** race conditions, lost updates, lock waits, retries/backoff,
latency waterfalls (critical path), batch vs stream, GC pauses.
```html
<div class="lanes" style="--label:220px">
  <div class="lane"><div class="lane-label">Request A<small>tx 1</small></div>
    <div class="lane-track">
      <div class="blk a-grow-x" data-step="1" style="--at:.02;--len:.22">READ stock=1</div>
      <div class="blk problem a-grow-x" data-step="3" style="--at:.40;--len:.22">WRITE stock=0</div>
    </div></div>
  <div class="lane"><div class="lane-label">Request B<small>tx 2</small></div>
    <div class="lane-track">
      <div class="blk a-grow-x" data-step="2" style="--at:.12;--len:.22">READ stock=1</div>
      <div class="blk problem a-grow-x a-shake" data-step="4" style="--at:.55;--len:.22">WRITE stock=0</div>
    </div></div>
  <div class="lane-mark" data-step="4" style="--at:.55"><span>bán 2, kho có 1</span></div>
  <div class="lane-axis"><span style="--at:0">0 ms</span><span style="--at:.5">50 ms</span><span style="--at:1">100 ms</span></div>
</div>
```
**Steps:** follow wall-clock order across lanes, not lane by lane. Then
a second slide (or a `.stack` swap) shows the fixed timeline.

## walkthrough — step through data or a structure
**When:** index seek, B-tree descent, hash ring lookup, binary search,
sort/merge, an `EXPLAIN` plan, pagination cursor movement.
```html
<div class="cols-2-1">
  <table class="tbl mono">
    <thead><tr><th>shop_id</th><th>status</th><th class="num">total</th><th class="num">id</th></tr></thead>
    <tbody>
      <tr class="a-dim" data-step="1"><td>41</td><td>PAID</td><td class="num">…</td><td class="num">…</td></tr>
      <tr class="a-focus" data-step="2"><td>42</td><td>PAID</td><td class="num">9.800.000</td><td class="num">91002</td></tr>
      <tr class="gap"><td colspan="4">… 49 dòng tiếp theo, đã đúng thứ tự …</td></tr>
    </tbody>
  </table>
  <div class="col">
    <div class="card flat a-left" data-step="1"><div class="h">① Nhảy tới shop 42</div><p class="small">…</p></div>
    <div class="card flat a-left" data-step="2"><div class="h">② Đã sắp sẵn theo total</div><p class="small">…</p></div>
  </div>
</div>
```
Use `data-focus` on the section for spotlight. Use `.pin`s inside a
`position:relative` wrapper as a moving cursor.
**Steps:** one narrowing per step; dim what's ruled out.

## window — a viewport over a big collection
**When:** virtual scroll, pagination window, sliding-window rate limit,
TCP window, Kafka consumer offset, LRU working set.
```html
<div class="cols-2-1">
  <div style="position:relative">
    <table class="tbl mono">… rows …</table>
    <div class="frame a-fade" data-step="1" style="top:180px;height:300px"><span>đang hiện</span></div>
  </div>
  <div class="col">
    <div class="stat problem"><span class="stat-value a-count" data-step="1" data-to="2350">0</span><span class="stat-label">dòng trong DOM</span></div>
  </div>
</div>
```
**Steps:** scroll (move the frame via a `.stack` swap or a second frame),
stats count, then the fix.

## code — annotated code or a diff
**When:** the change is the point: a query, a config, a fix.
```html
<div class="code" data-file="orders.sql">
  <span class="line"><span class="kw">SELECT</span> * <span class="kw">FROM</span> orders</span>
  <span class="line"><span class="kw">WHERE</span> shop_id = <span class="num">42</span><span class="ann" data-step="1">← lọc theo shop</span></span>
  <span class="line a-focus" data-step="2"><span class="kw">ORDER BY</span> total <span class="kw">DESC</span>, <span class="hot">id DESC</span><span class="ann focus">← tie-breaker</span></span>
  <span class="line"><span class="kw">LIMIT</span> <span class="num">50</span></span>
</div>
```
Diff: `<div class="code diff">` with `.line.add` / `.line.del`. Typing:
wrap a line's text in `<span class="a-type" data-step="1" style="--n:38">`.
≤ 14 lines; highlight with `.hot` / `.bad` / `.good` tokens, not by
coloring whole lines unless the line is the point.
**Steps:** annotate line by line in execution order.

## mapping — control → mechanism → verdict
**When:** "each UI choice/API param/config value implies a backend
requirement": sort dropdown → ORDER BY → index exists?; feature flag →
code path; HTTP verb → idempotency.
```html
<div class="cols-3" style="grid-template-columns:1fr 1.2fr .8fr;align-items:center">
  <div class="menu">
    <div class="menu-item">Ngày tạo: mới nhất</div>
    <div class="menu-item is-selected">Tổng tiền: cao → thấp</div>
  </div>
  <div class="col">
    <div class="flow" data-step="1"><i class="arrow"></i><span class="chip">created_at DESC</span></div>
    <div class="flow" data-step="2"><i class="arrow focus"></i><span class="chip focus">total DESC</span></div>
  </div>
  <div class="col">
    <span class="chip fix" data-step="1">✓ có index</span>
    <span class="chip problem a-pop" data-step="2">✗ filesort</span>
  </div>
</div>
```
**Steps:** one mapping row per step; the gap lands last.

## numbers — back-of-envelope math
**When:** capacity estimation, cost, "why 2.350 rows", "is this even a
problem?". The arithmetic *is* the content.
```html
<div class="row" style="align-items:stretch">
  <div class="stat grow"><span class="stat-value a-count" data-step="1" data-to="2000000">0</span><span class="stat-label">đơn / shop</span></div>
  <div class="center strong" style="font-size:56px">÷</div>
  <div class="stat grow" data-step="2"><span class="stat-value">50</span><span class="stat-label">đơn / trang</span></div>
  <div class="center strong" style="font-size:56px">=</div>
  <div class="stat problem grow a-pop" data-step="3"><span class="stat-value">40.000</span><span class="stat-label">trang</span></div>
</div>
```
**Steps:** operands in order, result `a-pop` last. Every number traces to
the fact sheet.

## bars — measured comparison
**When:** latency p50/p99, throughput, rows read, memory, cost per month.
```html
<div class="bars">
  <div class="bar"><div class="bar-label">OFFSET<small>trang 40.000</small></div>
    <div class="bar-track"><div class="bar-fill problem a-grow-x" data-step="1" style="--v:.94"></div></div>
    <div class="bar-value">2,1 s</div></div>
  <div class="bar"><div class="bar-label">Keyset</div>
    <div class="bar-track"><div class="bar-fill fix a-grow-x" data-step="2" style="--v:.02"></div></div>
    <div class="bar-value">4 ms</div></div>
</div>
```
Scale `--v` against the max on the slide; say so if the axis is log.
Label measured numbers with their conditions in the notes (or `.tiny`).

## failure — blast radius
**When:** what breaks when X dies / slows: SPOF, cascading retries, thundering
herd, replica lag, cache stampede, split brain.
Use the `trace` markup; at step n mark the failing node `a-problem a-shake`,
switch its wires `a-dim`, send `.packet.problem` retries to the neighbor with
`--loop:infinite`, then light the neighbor `a-problem`. End with the
mitigation (circuit breaker, jitter, bulkhead) as a `split` or swap.

## dialogue — two voices
**When:** the pivot ("why are we doing this?"), user intent, a code review
question, an interview question. Keeps the human in the story.
```html
<div class="cols-2">
  <div class="card"><span class="badge soft">NEWSFEED</span>
    <div class="chat">
      <div class="msg" data-step="1"><span class="avatar">S</span><div class="bubble">Em lướt newsfeed để làm gì?</div></div>
      <div class="msg me" data-step="2"><span class="avatar">J</span><div class="bubble">Để giải trí, lướt xem có gì hay.</div></div>
    </div></div>
  <div class="card"><span class="badge info">ADMIN ĐƠN HÀNG</span>…</div>
</div>
```
≤ 4 bubbles per column. A UI mock can sit inside the thread as the "answer".

## ask — predict pause
**When:** before a reveal. Alone (big, centered) or as the last block of a
slide.
```html
<div class="ask a-pop" data-step="3">
  <div><div class="ask-text">Lọc theo shop, lọc PAID, sort theo total — index thế nào?</div>
  <div class="ask-hint">Dừng video, thử viết ra thứ tự cột trước khi xem tiếp.</div></div>
</div>
```
The block is a solid ink panel with an amber `?` — the strongest contrast
on any slide, so use it only for real pauses. A placeholder in the content
(`( ? , ? , ? )` as `.chip`s) makes the question concrete. The answer is
never on the same slide.

## checklist — known vs not asked
**When:** the pivot: "technically done, but…" — what we verified vs what
we assumed. Pairs with a row of numbered question cards.
```html
<div class="cols-2">
  <div class="card fix flat"><span class="badge fix">ĐÃ CÓ · KỸ THUẬT</span>
    <span class="chip fix">✓ Keyset seek thẳng tới chỗ cần đọc</span> …</div>
  <div class="card problem flat"><span class="badge problem">CHƯA HỎI · NGƯỜI DÙNG</span>
    <div class="h">CS mở màn này để làm gì?</div> …</div>
</div>
<div class="cols-4">
  <div class="card flat" data-step="1"><span class="item-n">1</span><div class="h">Lướt hay tìm?</div></div> …
</div>
```

## list — numbered fits / cases / hypotheses
**When:** "where X fits", 3–5 hypotheses (strike the wrong ones),
use cases with real-world examples as `.tag`.
```html
<div class="items">
  <div class="item" data-step="1"><span class="item-n">1</span>
    <div><div class="item-title">Export, job quét hết bảng</div><div class="item-text">Đi từ đầu tới cuối, không nhảy trang.</div></div>
    <span class="tag">export</span></div>
</div>
```
For hypotheses: add `a-strike` on `.item-title` at the step it's ruled out.

## matrix — the trade-off table
**When:** after the mechanisms are shown — summarizing, never instead of.
```html
<table class="tbl matrix">
  <thead><tr><th></th><th>OFFSET</th><th>Keyset</th></tr></thead>
  <tbody>
    <tr data-step="1"><td class="strong">Trang sâu</td><td class="no">chậm dần</td><td class="yes win">hằng số</td></tr>
    <tr data-step="2"><td class="strong">Nhảy tới trang 37</td><td class="yes win">được</td><td class="no">không</td></tr>
  </tbody>
</table>
```
≤ 6 rows. End with a `callout info` holding the decision rule.

## pipeline — stages and the bottleneck
**When:** "where does the time go": read → filter → sort → page; build →
test → deploy; ingest → transform → load. Two parallel pipelines compare
variants; the shared bottleneck is the punchline.
```html
<div class="col gap-lg">
  <div class="flow">
    <span class="badge soft">OFFSET</span><i class="arrow"></i>
    <div class="box problem grow">Đọc hết 2 triệu đơn<small>không có index đúng thứ tự</small></div><i class="arrow"></i>
    <div class="box grow">Heap giữ OFFSET + 50<small>…</small></div><i class="arrow"></i>
    <div class="box fix">50 dòng</div>
  </div>
  <div class="flow" data-step="1">…same stages for KEYSET…</div>
</div>
```
**Steps:** second pipeline → the shared slow stage `a-pulse` → verdict.

## state — a state machine
**When:** order lifecycle, circuit breaker, TCP, Raft roles, job retries.
Use the `trace` diagram with `.node.state` pills and curved wires
(`d="M… C…"`) labeled with events. Steps: walk one entity through its
states; the illegal transition gets `wire problem` + `✗`.

## recap — what to keep
**When:** last slide, optional. 3–5 takeaways, each one a decision rule or
a "watch out", with the slide number it came from.
```html
<div class="items">
  <div class="item fix"><span class="item-n">1</span><div><div class="item-title">Index quyết định, không phải kiểu phân trang</div></div><span class="tag">slide 14</span></div>
</div>
```

---

### Composition rules

- One archetype per slide; at most one secondary (an `ask` block, a
  `stat` column, a callout row).
- Two-column slides: keep both columns the same archetype so the eye can
  compare row by row.
- A deck uses at least 5 different archetypes — a wall of `split`s reads
  as a document.
