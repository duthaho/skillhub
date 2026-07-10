# HTML brief design brief — the input for the `frontend-design` skill; read it when designing the .html output.

- **Brief for the designer:** the subject is *this topic and its community
  conversation*; the audience is someone scanning "what's happening now"; the page's
  one job is to make the TL;DR, ranked Key Developments, Best Takes, and
  Disputed/Unconfirmed items instantly scannable, with engagement metrics as
  first-class visual elements. Ground the aesthetic in the topic's own world (a dev
  tool, a person, a cultural event each suggest a different visual identity) so no two
  briefs look alike.
- **Hard constraints (pass these to `frontend-design`):** single self-contained
  `.html` file, **inline CSS only, no JavaScript, no external requests/CDNs/web
  fonts** (system font stack), keep all source links and engagement numbers, must be
  readable on mobile and when printed, and **must include every section** of the
  brief template (header with sources-reached, TL;DR, Since last pulse when
  present, Key Developments, Best Takes, Disputed/Unconfirmed, Sources) with the
  exact same content as the `.md`.
- Render the markdown brief content faithfully into that design — design changes the
  presentation, never the facts, citations, or engagement metrics.
