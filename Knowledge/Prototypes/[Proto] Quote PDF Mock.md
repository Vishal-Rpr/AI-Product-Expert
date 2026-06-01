# [Proto] Quote PDF Mock

## Context
HTML mock of the SILQ Quote PDF (SILQ-4228268Q1) used to visualize two proposed changes to the quote document layout before implementing in the actual PDF generation system.

## Changes Mocked
1. **Added `*` next to "EST. TOTAL TRANSIT TIME"** on Page 1 — to flag that transit time is an estimate subject to conditions.
2. **Added footnote after Terms & Conditions** on Page 4 — `* Final routing subject to space availability/Carrier approval.`

Both changes are highlighted in yellow with a dashed border for easy identification.

## File Location
`Prototypes/quote-pdf-mock.html`

## How to Use
Open the HTML file in any browser. All 4 pages of the quote are rendered vertically. A sticky banner at the top calls out the 2 changes. Highlighted sections use a yellow background with dashed amber border.

## Original PDF
Source: `Quote PDF.pdf` (SILQ-4228268Q1 — CNYTN > Fajardo WH, Vandelay Industries)
