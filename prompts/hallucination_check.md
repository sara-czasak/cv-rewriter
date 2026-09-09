You are checking whether a rewritten CV is truthful relative to the
candidate's original base CV, which is the sole source of truth.

BASE CV (source of truth):
{base_cv}

REWRITTEN CV (to check):
{new_cv}

Check whether every claim in the rewritten CV — job titles, dates,
skills, achievements, and metrics — is supported by the base CV. Flag
anything invented, exaggerated, or not present in the base CV as a
hallucination. Rephrasing or reordering existing content is NOT a
hallucination; only flag genuinely new or unsupported claims.

Respond in this exact format (no brackets around the values):
TRUTHFUL: <TRUE or FALSE>
REASONING: <explanation of any discrepancies found, or confirmation
none were found>
