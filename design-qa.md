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

## Intentional Deviations

- BrickSeek keeps its own left-aligned brand and settings controls instead of copying the mini program title bar.
- Prize draws, auctions, ownership counts, and market charts were not copied because BrickSeek does not yet have reliable backing data for those features.
- Theme entries use text marks rather than copied third-party logo artwork.
- Mobile result cards use two columns instead of three so bilingual names remain readable.

## Interaction Verification

- Home actions, theme searches, bottom navigation, text search, category tabs, sorting, detail navigation, assemble/explode, part images, and full-screen camera were exercised.
- Camera is full viewport, the dashed guide is visible, the shutter is 76px, local upload remains hidden, and the site navigation is hidden while scanning.
- The dark gold theme still renders without overflow.

Final result: passed
