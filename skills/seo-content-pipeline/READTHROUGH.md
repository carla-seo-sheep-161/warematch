# Mandatory human read-through (stage 7) — read the WHOLE draft against this list before any import or sheet write
Automated gates cannot see reader experience. Every item below came from a real miss in the Shopify, warehouse-space, USA and Florida runs.
1. **Stat dumps / so-what**: every figure must change a decision; 1-2 rounded headline figures per point; split long mixed-number sentences. (USA labor paragraph.)
2. **Repetition across sections**: facts, county/state lists, storm plans, WareMatch pitch must appear once; later sections point back or add something new. (Florida counties in an FAQ; storm plan in 4 places.) `audit.py` 3c flags shared names/figures.
3. **Audience assumptions**: general 3PL pages serve parcel, pallet, wholesale, retail, cold chain; e-commerce wording only where the query/section is about online sellers. (USA cost FAQ.)
4. **Unsupported or invented claims**: no uncited numbers/thresholds; no claims the source did not make (say 'commercial rentals', not 'warehouses', if the PDF could not be read); remove own-wording filler ('hidden fees usually sit...').
5. **Easy-terms sweep done**: `optimize.py` prints basic/extended term coverage; basic must be >=90% before declaring any ceiling; skip only brand/ranking/competitor/generic-filler terms. (Florida: 8 basic terms missed.)
6. **Headings**: start with a capital; keep exact-case replacements (a case-insensitive replace lowercased an FAQ heading).
7. **WareMatch connection** (location pages): tie each local decision to a real WareMatch action (capability filter, city filter, one request listing destination cities / entry port / storm needs). Never invent network counts; add real Florida/state listing facts only when the data exists.
8. **Links**: topical authored links (industry/guide pages), location links come from the template, max 5, none in TL;DR/takeaways (blog 'recommended first' structure allows the RFQ button only).
9. **Template**: locked copy verbatim, H2 order, H3 counts, sentence limits (check_page.py modes: industry, blog, location, state).
10. **Sources**: every primary-source claim re-read by the lead; unreadable PDFs and agent-only claims are NOT used; competitors and companies that sell warehousing/3PL/space are never cited.
11. **Keyword/brief choice**: sheet primary vs GSC reality (`keyword_check.py`) and SERP intent (landlord/listing vs 3PL services) decided BEFORE drafting.
12. **Etiquette**: never import into a NeuronWriter brief the owner is editing; fill only EMPTY sheet output cells; never overwrite owner entries.
