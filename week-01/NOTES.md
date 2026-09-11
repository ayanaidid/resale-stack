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

---
Friday, Sept 4, 2026
Numbers export went to iCloud, not the repo → macOS "Desktop & Documents
  in iCloud" makes ~/Documents an iCloud location. Numbers defaulted its
  export there, silently creating a parallel resale-stack/week-01/data/
  path. The overwrite prompt was real — but for the wrong file. Lesson:
  an overwrite confirmation only proves a file with that name existed
  where you're saving, not that you're saving in the right place. Verify
  with a timestamp check, not the dialog.

---
Wednesday, Sept 9, 2026
Price fields → market_price = platform's retail estimate. original_price =
  pre-discount asking price on this platform, blank if not discounted.
  listed_price = current asking price, always populated. Three distinct
  concepts; platforms use inconsistent labels for all three.

---
Thursday, Sept 10, 2026
CLI — command-line interface. A program you run by typing its name in the terminal, rather than clicking an icon or opening a
  webpage. hello.py was already one: you typed python3 hello.py and it did its thing and printed output. That's it. "Build a Python CLI" just means "build a script I run from the terminal." No windows, no buttons.

DictReader — a tool from Python's built-in csv module for reading CSV files. The key part is what it hands you. A plain CSV reader    
  gives you each row as a list, so you'd access fields by position. DictReader reads your header row first and gives you each row as a dictionary, so you access fields by name.

Stub — a function that exists but doesn't do anything yet. A placeholder with the right name and shape, so the surrounding code can 
  call it, but with the actual logic left empty.

Silent skip vs auto-clean → load_done_ids skips unparseable lines and
  reprocesses that listing. Correct for resumability. Chose to add a
  warning print rather than auto-rewriting the file on startup: read
  operations shouldn't mutate data, and a rewrite that gets interrupted
  can lose good results to fix a cosmetic problem.

flush() → out.write() only puts bytes in Python's buffer; the OS gets
  them when the buffer fills or the file closes. Crash mid-run = those
  writes are lost, even though the API call succeeded and was billed.
  flush() after each write costs a little performance and caps the loss
  at one row. Buffering is invisible until it isn't.

From the docs block:
Tool definition requires name, description, input_schema with properties and required. The description field is read by the model and affects extraction quality — it's a tunable knob, not documentation.
Structured output arrives in a tool_use block, in its input field, as a dict. Same content-block loop as hello.py, different block type — text is block.text, tool use is block.input.
The model doesn't error on fields it can't fill. It guesses. No exception, no warning. This is why failures are silent and why the eval exists.
enum constrains output to a fixed list — you'll always get one of your five tiers. Format guarantee, not correctness guarantee.

From the scaffolding block:
The three you interrogated: silent-skip on malformed JSONL, fail-fast on non-API exceptions vs retry-with-backoff on anthropic.APIError, and flush() capping crash loss at one row.
The .gitignore incident — Claude Code fused *.pyc and .DS_Store into *.pyc.DS_Store, a line matching nothing. And it gitignored extractions.jsonl on a sensible default ("generated output isn't source") that conflicted with a goal it didn't know: the outputs are the deliverable.
The summary-vs-file gap — twice, the model described a change whose displayed evidence didn't clearly support it. Verify the file, not the summary. That's a durable working rule, not a one-off.
Terminology: CLI, DictReader, stub — if those were new today, they belong in there.

Model defaults can conflict with project goals silently → Claude Code
  gitignored extractions.jsonl because generated output isn't source.
  Standard convention, correct in general, wrong here — the outputs are
  the Week 1 deliverable. Nothing was buggy; it just didn't know the
  purpose. Review generated decisions against intent, not just
  correctness.

"Insufficient information" = 10/30 → not a bug. stated_condition was
  deliberately excluded from the prompt so condition_tier measures
  inference, not transcription. These ten have condition only in a
  structured field; their descriptions are attribute soup (Size/Color/
  Brand dumps), not prose. A third of listings carry no condition signal
  in text at all.

---
Friday, Sept 11, 2026
Condition signal location varies by platform → TRR 4/6 and Vinted 3/5
  ungradeable from description alone; eBay 0/5. TRR and Vinted put
  condition in structured fields and leave descriptions as attribute
  dumps. Not a pipeline bug — stated_condition was excluded by design.
  Small n; Week 3 tests whether it holds.

Cost structure inverted from expectation → output tokens cost 5x input,
  but with a ~1,000-token system prompt and ~2,000-token listings,
  input is ~78% of per-call cost. The "make the model say less" lever
  doesn't apply here; the lever is caching the system prompt (identical
  across all 30 calls) and trimming boilerplate from descriptions.