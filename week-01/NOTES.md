# NOTES.md — Week 1

Format: construct/error → what it turned out to mean

---
Sunday, Aug. 30th, 2026:
cat -A → GNU/Linux flag for showing hidden characters (line endings, etc). 
  Doesn't exist on macOS's cat (BSD). macOS equivalent is cat -e.

.env parsing → python-dotenv splits each line on the first `=` sign to get
  variable name and value. If the line is just the raw key with no
  `ANTHROPIC_API_KEY=` prefix, dotenv has nothing to assign it to, so
  os.environ.get() silently returns None — no error, just a missing value.
  This is why the API call failed with a vague auth error instead of
  something obviously pointing at .env.

find_dotenv() → the function load_dotenv() calls internally to locate the
  .env file. Calling it directly and printing the result is a good way to
  check "is the file even being found" separately from "is the file being
  parsed correctly" — two different failure modes that look identical
  from the outside.

Invalid model name → 404, not 400. The API treats the model as part of
  routing/lookup, not just a field to validate. A misspelled model name
  behaves like hitting a URL that doesn't exist, not like sending bad data.

Missing max_tokens → TypeError raised locally by the SDK, not a server
  error. The client validates required args (max_tokens, messages, model)
  before sending anything over the network. Different failure shape than
  the bad model name, which had to round-trip to the API to fail.

String instead of int for max_tokens → TypeError, but NOT caught upfront
  like the missing-argument case. Python doesn't check types until a
  value is actually used in an operation that requires one — here, string
  division three function calls deep inside an internal timeout
  calculation. Presence-checking and type-checking are different things;
  the SDK does the first eagerly and not really the second.

---
Wednesday, Sept 2nd, 2026
1/2 of the seller lingo predictions aren't about wear at all — they're about why the seller chose that 
    specific phrasing. That's arguably a more interesting thing to test against the model than the condition 
    tier itself: does the model pick up on "vintage patina" as potential spin, or does it take the phrase at 
    face value?

Divergent branches → happens when you commit both locally and on
  GitHub's website. Git refuses to push because it can't know which
  history wins. Fix: git pull (merge), then push. Prevention: pick one
  place to edit, don't do both.

vim → git's default editor for commit messages. Modal: keystrokes are
  commands, not text, unless you're in insert mode. :wq = write and quit,
  but only works in normal mode (Esc first). Swapped it for VS Code with
  git config --global core.editor "code --wait".

"Not committing merge; use git commit to complete" → the merge actually
  succeeded, only the message step failed. Merge state persists; finishing
  it is just git commit -m. Failure messages often describe a smaller
  problem than they look like.

raw_description convention → verbatim, including platform boilerplate,
  duplicated condition/size fields, and spec data (measurements,
  composition). Raw data files stay raw; stripping is a code step, not a
  collection step. Exception: collapse runs of whitespace to single
  spaces — those are a copy-paste artifact, not content.

Listing fields are redundant by design → Vestiaire repeats condition and
  size inside the description body as well as in structured fields. Means
  the model will see the condition label twice, which may make extraction
  look better than it would on a platform that doesn't duplicate. Worth
  checking whether other platforms do this before treating any accuracy
  number as comparable across sources.