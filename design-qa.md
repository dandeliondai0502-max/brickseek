# BrickSeek Collector UI Design QA

Reference: `/tmp/brickseek-ref-home.png`
Rendered implementation: `/tmp/brickseek-v7-home.png`
Viewport: 390 x 844

## Fidelity Ledger

| Area | Reference evidence | Render evidence | Result |
| --- | --- | --- | --- |
| Palette | White canvas with one yellow action color | White canvas, yellow action circles and scan button | Passed |
| Search | Full-width rounded search near the top | Full-width rounded search with camera action | Passed |
| Information density | Actions, themes, featured figures in the first viewport | Four actions, ten themes, three featured figures in the first viewport | Passed |
| Product imagery | Large minifigure photos dominate cards | Real minifigure photos dominate the featured rail and result cards | Passed |
| Navigation | Five-item fixed mobile navigation | Five-item fixed navigation with emphasized scan action | Passed |
| Spacing and geometry | Tight vertical rhythm, small radii, no decorative shadows | Tight rhythm, 8-10px radii, flat surfaces | Passed |
| Responsive behavior | Mobile-first composition with dense content | 390px mobile, 900px tablet, and 1440px desktop use separate grid arrangements with zero horizontal overflow | Passed |
| Split-screen detail | The supplied narrow desktop screenshot clips the assembly controls and shrinks the figure to mobile scale | Detail containers can shrink without overflow; 641-1180px uses a single-column detail layout and 641-720px enlarges the figure while retaining desktop navigation | Passed |
| Minifigure catalog geometry | Individual rounded cards feel disconnected | Search, catalog, and favorites use connected square cells with a single 1px divider | Passed |
| Minifigure imagery | Source photos use visibly different canvas colors and whitespace | Every figure uses the same square stage, neutral background, padding, bottom alignment, and light-theme blending | Passed |
| Minifigure names | Long names are clamped and end in an ellipsis | Names wrap to their full content on desktop and mobile without horizontal overflow | Passed |

## Intentional Deviations

- BrickSeek keeps its own left-aligned brand and settings controls instead of copying the mini program title bar.
- Prize draws, auctions, ownership counts, and market charts were not copied because BrickSeek does not yet have reliable backing data for those features.
- Theme entries use text marks rather than copied third-party logo artwork.
- Mobile result cards use two columns instead of three so bilingual names remain readable.

## Interaction Verification

- Home actions, theme searches, bottom navigation, text search, category tabs, sorting, detail navigation, assemble/explode, part images, and full-screen camera were exercised.
- The `IG-88, Round Plate Head` search-to-detail flow was rerun after the split-screen fix; both assembly controls remain available and explode reveals all seven parts.
- The catalog was checked at 1280 x 800 and 390 x 844: cards have 0px radius and 1px connected dividers; the longest sampled name has equal client and scroll heights, with no line clamp.
- Minifigure image hover was checked after the catalog revision: computed transform remains `none` and transition duration is `0s`, so pointer entry and exit cannot resize the figure.
- Camera is full viewport with no figure outline, focus target, framing overlay, or guide copy; the shutter is 76px, local upload remains hidden, and the site navigation is hidden while scanning.
- Camera photos are sent directly to Brickognize's minifigure model; the UI displays only returned candidates and asks the user to retake the photo when no reliable result is available.
- At 390 x 844, the open camera modal has zero outline, guide-copy, or simulated bounding-box nodes and the document scroll width remains exactly 390px.
- The local `/api/scan-image` gateway was exercised with a public Darth Vader image: Brickognize returned `sw0218`, which resolved to local record `fig-000581` at 81.1% confidence.
- Long character names wrap to their full text. At 920px, `Spectral Dragonian Warrior, Ghost Lower Body, Wings` is unclipped and all nine parts occupy nine distinct list rows.
- Each exploded-part row contains its sequence number, real image, full name, and part number. The list grows with the part count without touching the footer; the same nine-row structure remains unclipped at 390px.
- Camera recognition sends one photo directly from the browser to Brickognize and immediately uses its top minifigure result without the BrickSeek recognition gateway, local scoring thresholds, consensus voting, or a second AI model.
- The dark gold theme still renders without overflow.

Final result: passed
