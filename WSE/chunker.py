def chunk_text(text, max_chars=8000, overlap=500):
    """
    Split manuscript text into manageable overlapping chunks.

    We use characters for the prototype rather than tokens so that
    we don't need a tokenizer dependency yet.
    """

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_chars, text_length)

        # Prefer ending at a paragraph boundary.
        if end < text_length:
            paragraph_break = text.rfind("\n\n", start, end)

            if paragraph_break > start + (max_chars * 0.5):
                end = paragraph_break

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(0, end - overlap)

    return chunks