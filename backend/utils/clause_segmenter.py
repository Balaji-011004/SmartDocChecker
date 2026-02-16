"""
Clause Segmentation Utility — Sentence-Level

Extracts **complete sentences** from document text for contradiction detection.
Only sentences that make an assertive claim (contain a verb, proper structure)
are kept.  Fragments, headings, page headers, and boilerplate are discarded.

Pipeline:
  1. Strip section-heading numbering noise
  2. Split into candidate sentences (period / semicolon boundaries)
  3. Clean each candidate (trim numbering prefixes, whitespace)
  4. Validate: must be a proper sentence (verb, length, not noise)
  5. Near-duplicate collapse (≥85 % word overlap → keep first)
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# ── Pre-compiled patterns for noise detection ──
_RE_PAGE_NUMBER     = re.compile(r'^(?:page\s+)?\d+(?:\s*(?:of|/)\s*\d+)?$', re.IGNORECASE)
_RE_URL             = re.compile(r'^https?://', re.IGNORECASE)
_RE_TOC_ENTRY       = re.compile(r'\.{3,}\s*\d+$')
_RE_DATE_ONLY       = re.compile(
    r'^(?:date[:\s]*)?'
    r'(?:\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|'
    r'(?:january|february|march|april|may|june|july|august|september|october|november|december)'
    r'\s+\d{1,2},?\s*\d{2,4}|'
    r'\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)'
    r',?\s*\d{2,4})$',
    re.IGNORECASE,
)
_RE_NUMERIC_ROW     = re.compile(
    r'^[\d\s\.\,\$\%\€\£\(\)\-\+\/\|:]+$'
)
_RE_SIGNATURE_LINE  = re.compile(
    r'^(?:(?:signed|signature|authorized|approved|witnessed|notarized)'
    r'(?:\s+by)?[:\s]|_{3,}|\.{3,}\s*$)',
    re.IGNORECASE,
)
_RE_COPYRIGHT       = re.compile(
    r'(?:©|\(c\)|copyright|all\s+rights\s+reserved|confidential\s+and\s+proprietary)',
    re.IGNORECASE,
)
_RE_HEADER_FOOTER   = re.compile(
    r'^(?:private\s+&?\s*confidential|draft|for\s+internal\s+use\s+only'
    r'|strictly\s+confidential|do\s+not\s+distribute'
    r'|privileged\s+and\s+confidential'
    r'|prepared\s+(?:by|for)[:\s]'
    r'|document\s+(?:no|number|ref|reference|id|version)[:\s#]'
    r'|rev(?:ision)?[:\s\.]?\s*\d'
    r'|version[:\s\.]?\s*\d'
    r'|effective\s+date[:\s]'
    r'|last\s+(?:updated|modified|revised)[:\s])',
    re.IGNORECASE,
)
_RE_DISCLAIMER      = re.compile(
    r'(?:this\s+document\s+is\s+(?:provided|furnished)\s+(?:as\s+is|for\s+information)'
    r'|(?:no|without)\s+(?:warranty|guarantee|representation)'
    r'|for\s+informational\s+purposes\s+only'
    r'|e\.?\s*&?\s*o\.?\s*e\.?'
    r'|errors?\s+and\s+omissions?\s+excepted)',
    re.IGNORECASE,
)
_RE_TABLE_HEADER    = re.compile(
    r'^(?:(?:sr\.?\s*no|s\.?\s*no|sl\.?\s*no|#|item|description|qty|quantity'
    r'|amount|total|subtotal|unit|rate|price|cost|value|balance'
    r'|debit|credit|particulars|remarks?)\s*[\|\t,]){2,}',
    re.IGNORECASE,
)
_RE_BOILERPLATE     = re.compile(
    r'^(?:'
    r'this\s+(?:section|chapter|report|document|annex|appendix|part)\s+(?:describes|outlines|provides|presents|discusses|covers|deals\s+with|sets\s+out|contains|summarizes|explains|focuses|examines)'
    r'|for\s+the\s+purposes?\s+of\s+this\s+(?:document|report|agreement|policy|standard|guideline)'
    r'|the\s+following\s+(?:section|table|figure|chart|diagram|list|annex|appendix)'
    r'|as\s+(?:described|defined|outlined|mentioned|noted|discussed|stated|specified|indicated|shown|illustrated)\s+(?:in|above|below|earlier|previously)'
    r'|(?:see|refer\s+to)\s+(?:section|chapter|annex|appendix|table|figure|paragraph|page|clause)'
    r'|in\s+accordance\s+with\s+(?:section|clause|article|annex|appendix)'
    r'|note[:\s]'
    r'|source[:\s]'
    r')',
    re.IGNORECASE,
)
_RE_CITATION        = re.compile(
    r'(?:'
    r'\[\d+\]'
    r'|\((?:(?:19|20)\d{2}[a-z]?(?:;\s*)?)+\)'
    r'|\b(?:ibid|op\.?\s*cit|et\s+al)\.?'
    r'|^\d+\.\s+[A-Z][^.]{5,60}\.\s+(?:(?:19|20)\d{2})'
    r')',
    re.IGNORECASE,
)
_RE_LIST_INTRO      = re.compile(
    r'^.*(?:as\s+follows|the\s+following|includes?\s+(?:the\s+following|but\s+not\s+limited\s+to)|such\s+as|for\s+example|e\.g\.|i\.e\.)[:\s]*$',
    re.IGNORECASE,
)
_RE_CHAPTER_HEADING = re.compile(
    r'^(?:'
    r'(?:chapter|part|module|unit|volume|phase|stage|annex|appendix)\s*[-–—:]?\s*\d+'
    r'|\d+\.\s*(?:introduction|conclusion|summary|overview|background|methodology|results|discussion|analysis|objectives?|scope|limitations?|recommendations?)'
    r'|(?:abstract|acknowledgements?|preface|foreword|executive\s+summary|list\s+of\s+(?:figures|tables|abbreviations))'
    r')\s*$',
    re.IGNORECASE,
)
_RE_RUNNING_HEADER  = re.compile(
    r'(?:'
    r'\|\s*\d{1,4}\s'          # "Company | 3 Title"
    r'|^\d{1,4}\s+[A-Z]'       # "3 Forecasting Crypto..."
    r'|[A-Z][^|]{5,}\|\s*\d'   # "Title Text | 7"
    r')',
)
_RE_HAS_VERB        = re.compile(
    r'\b(?:'
    r'is|are|was|were|be|been|being|am'
    r'|have|has|had|having'
    r'|do|does|did|doing'
    r'|will|would|shall|should|may|might|can|could|must'
    r'|include[sd]?|contain[sd]?|consist[sd]?|comprise[sd]?'
    r'|provide[sd]?|require[sd]?|specify|specifies|specified'
    r'|state[sd]?|define[sd]?|describe[sd]?|indicate[sd]?'
    r'|allow[sd]?|permit[sd]?|prohibit[sd]?|restrict[sd]?'
    r'|ensure[sd]?|maintain[sd]?|establish(es|ed)?'
    r'|determine[sd]?|affect[sd]?|impact[sd]?|influence[sd]?'
    r'|increase[sd]?|decrease[sd]?|reduce[sd]?|improve[sd]?'
    r'|exceed[sd]?|remain[sd]?|occur[sd]?|exist[sd]?'
    r'|operate[sd]?|function[sd]?|perform[sd]?'
    r'|submit[sd]?|report[sd]?|recommend[sd]?'
    r'|manage[sd]?|monitor[sd]?|assess(es|ed)?'
    r'|predict[sd]?|estimate[sd]?|measure[sd]?'
    r'|implement(ed|s)?|apply|applies|applied'
    r'|use[sd]?|using|employ[sd]?'
    r'|demonstrate[sd]?|show[sd]?|suggest[sd]?'
    r'|result[sd]?|cause[sd]?|lead[sd]?|contribute[sd]?'
    r')\b',
    re.IGNORECASE,
)

# Words that mark boilerplate sections we should skip entirely
_SKIP_SECTION_TITLES = {
    'table of contents', 'contents', 'index', 'appendix',
    'glossary', 'definitions', 'abbreviations', 'acronyms',
    'references', 'bibliography', 'attachments', 'annexure',
    'signature page', 'execution page', 'witness',
}


def segment_clauses(raw_text: str) -> List[str]:
    """
    Extract complete, assertive sentences from document text.

    Only keeps text that:
      • Contains a verb (makes a claim)
      • Has ≥ 8 words
      • Ends with sentence-ending punctuation (. ? ! ;) or is long enough
      • Is not a heading, header, footer, boilerplate, or data row

    Returns:
        Ordered list of unique sentence strings.
    """
    if not raw_text or not raw_text.strip():
        return []

    sentences: List[str] = []
    in_skip_section = False

    # ── 1. Split by major section headings ──
    section_pattern = r'(?:^|\n)(?:(?:\d+\.)+\s+|(?:Article|Section|Chapter|Part)\s+\d+[:\.]?\s+)([^\n]+)'
    sections = re.split(section_pattern, raw_text, flags=re.MULTILINE | re.IGNORECASE)

    for i, chunk in enumerate(sections):
        if not chunk or not chunk.strip():
            continue

        # Odd indices are captured heading text
        if i % 2 == 1:
            heading = chunk.strip().lower()
            in_skip_section = any(skip in heading for skip in _SKIP_SECTION_TITLES)
            continue

        if in_skip_section:
            continue

        # ── 2. Split into bullet sub-chunks ──
        bullet_pattern = r'(?:^|\n)\s*(?:[•\-\*]|\d+[\.\)])\s+'
        bullet_chunks = re.split(bullet_pattern, chunk)

        for bc in bullet_chunks:
            if not bc or not bc.strip():
                continue

            # ── 3. Split by sentence boundaries ──
            #   . or ; or ? or ! followed by whitespace + uppercase letter
            #   or period/semicolon + newline / double-space
            sent_pattern = (
                r'(?<=[.;?!])\s*(?:\n|\s{2,})'      # punc + newline / 2+ spaces
                r'|(?<=[.?!])\s+(?=[A-Z])'           # punc + space + uppercase
            )
            raw_sents = re.split(sent_pattern, bc)

            for raw in raw_sents:
                cleaned = _clean_sentence(raw)
                if not cleaned:
                    continue
                if _is_noise(cleaned):
                    continue
                if not _is_sentence(cleaned):
                    continue
                sentences.append(cleaned)

    # ── 4. Near-duplicate collapse ──
    unique = _deduplicate(sentences)

    logger.info(f"Segmented {len(unique)} sentences from {len(raw_text)} characters")
    return unique


# ─────────────────────────────────────────────────────────────────────────────
#  Sentence validation
# ─────────────────────────────────────────────────────────────────────────────

def _clean_sentence(raw: str) -> str:
    """Trim leading numbering, bullet markers, and excess whitespace."""
    s = raw.strip()
    # Strip leading "1.2.3 " or "a) " or "iv. "
    s = re.sub(r'^(?:\d+\.)+\s*', '', s)
    s = re.sub(r'^[a-z]\)\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^(?:i{1,3}|iv|vi{0,3}|ix|x{1,3})[\.\)]\s+', '', s, flags=re.IGNORECASE)
    # Collapse whitespace
    s = ' '.join(s.split())
    return s


def _is_sentence(text: str) -> bool:
    """
    Return True only if *text* looks like a complete, assertive sentence.

    Requirements:
      1. At least 8 words
      2. Contains a verb (checked via _RE_HAS_VERB)
      3. Starts with an uppercase letter or a digit
      4. Not purely a heading / title (all caps + short)
    """
    words = text.split()
    if len(words) < 8:
        return False

    # Must contain a verb → makes a claim
    if not _RE_HAS_VERB.search(text):
        return False

    # Must start with uppercase letter, digit, or opening quote
    if not re.match(r'^[A-Z0-9"\'\(]', text):
        return False

    return True


def _deduplicate(sentences: List[str]) -> List[str]:
    """
    Remove exact duplicates and near-duplicates (≥85 % word overlap).
    Preserves document order — keeps the first occurrence.
    """
    seen_norm: set = set()
    seen_word_sets: List[set] = []
    unique: List[str] = []

    _stop = frozenset({
        'the','a','an','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','of','in','to','for',
        'and','or','but','on','at','by','with','from','as','into',
        'that','this','it','its','not','no','if','so','than','then',
    })

    for sent in sentences:
        norm = ' '.join(sent.lower().split())

        # Exact dup
        if norm in seen_norm:
            continue
        seen_norm.add(norm)

        # Near-dup: ≥85 % content-word overlap with any already-kept sentence
        cw = {w for w in norm.split() if w not in _stop and len(w) > 2}
        is_near_dup = False
        for prev in seen_word_sets:
            if not cw or not prev:
                continue
            overlap = len(cw & prev) / max(len(cw), len(prev))
            if overlap >= 0.85:
                is_near_dup = True
                break
        if is_near_dup:
            continue

        seen_word_sets.append(cw)
        unique.append(sent)

    return unique


def _is_noise(text: str) -> bool:
    """
    Return True for text that should never be treated as a sentence for
    contradiction detection — headers, footers, data rows, boilerplate, etc.
    """
    stripped = text.strip()
    words = stripped.split()

    # ── Length checks ──
    if len(words) < 6:
        return True

    # ── Pattern checks ──
    if _RE_PAGE_NUMBER.match(stripped):
        return True

    if _RE_URL.match(stripped):
        return True

    if _RE_TOC_ENTRY.search(stripped):
        return True

    if _RE_DATE_ONLY.match(stripped):
        return True

    if _RE_NUMERIC_ROW.match(stripped):
        return True

    if _RE_SIGNATURE_LINE.match(stripped):
        return True

    if _RE_COPYRIGHT.search(stripped) and len(words) < 20:
        return True

    if _RE_HEADER_FOOTER.match(stripped):
        return True

    if _RE_DISCLAIMER.search(stripped) and len(words) < 30:
        return True

    if _RE_TABLE_HEADER.match(stripped):
        return True

    # ── Report boilerplate / definitional preamble ──
    if _RE_BOILERPLATE.match(stripped) and len(words) < 25:
        return True

    # ── Citations / references ──
    if _RE_CITATION.search(stripped) and len(words) < 20:
        return True

    # ── List introduction lines ("The following items:") ──
    if _RE_LIST_INTRO.match(stripped):
        return True

    # ── Chapter / section heading-only lines ──
    if _RE_CHAPTER_HEADING.match(stripped):
        return True

    # ── Running headers ("Institution | 3 Report Title") ──
    # If >40% of the text matches a running-header pattern and it's short, skip
    if _RE_RUNNING_HEADER.search(stripped) and len(words) < 15:
        return True

    # ── All caps header ──
    if stripped.isupper() and len(stripped) < 60:
        return True

    # ── Mostly numbers/symbols (> 60% non-alpha chars → likely a data row) ──
    alpha_chars = sum(1 for c in stripped if c.isalpha())
    if len(stripped) > 0 and alpha_chars / len(stripped) < 0.35:
        return True

    # ── Email / phone lines ──
    if re.match(r'^(?:email|e-mail|tel|phone|fax|mobile|contact)[:\s]', stripped, re.IGNORECASE):
        return True

    # ── Address-like lines (short, ends with zip code) ──
    if re.search(r'\b\d{5,6}\b$', stripped) and len(words) < 8:
        return True

    return False


def extract_section_heading(text: str, position: int) -> str:
    """
    Extract section heading from surrounding context.

    Args:
        text: Full document text
        position: Character position of the clause

    Returns:
        Section heading string or empty string
    """
    before_text = text[:position]
    section_pattern = r'(?:^|\n)((?:\d+\.)+\s+[^\n]+|(?:Article|Section|Chapter|Part)\s+\d+[:\.]?\s+[^\n]+)'
    matches = list(re.finditer(section_pattern, before_text, re.MULTILINE | re.IGNORECASE))

    if matches:
        return matches[-1].group(1).strip()

    return ""
