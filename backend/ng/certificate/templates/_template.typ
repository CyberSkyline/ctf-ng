#let certificate-template(
  // FONTS
  body-font: "Libertinus Serif",
  display-font: "Libertinus Serif",

  // uppercase headings & the event name
  capitalize-headings: true,

  // MAIN CONTENT AREA
  title: "Certificate of Completion",
  title-text-color: white,

  // render the subtitle (event or challenge name) as a heading instead of accent-colored text
  subtitle-as-heading: false,

  // page background visible underneath main content area
  bg-image: none,
  // tint applied on top of the image above
  bg-tint: gradient.linear(black, black.transparentize(25%)),

  // logo for top left corner
  primary-logo: none,
  // logo for top right corner
  secondary-logo: image("cisa.svg", alt: "CISA"),

  // SIDEBAR
  sidebar-text-color: black,
  sidebar-bg-color: white,

  // ACCENT STRIPE
  accent-color: red,

  // position the accent stripe against the right edge.
  // set true for background images that should blend into the sidebar background.
  stripe-on-outside: false,
) = {
  // Page & background configuration
  set page(
    paper: "presentation-16-9",
    margin: 0in,
    background: if bg-image != none [
      #set image(width: 100%, height: 100%, fit: "cover")
      #bg-image
    ] else [
      // if bg-image is not specified, use a solid color rect
      #rect(width: 100%, height: 100%, fill: bg-tint)
    ],
  )

  // Global text styles
  set text(font: body-font, size: 16pt)
  set par(linebreaks: "optimized")
  show heading: set text(font: display-font, size: 16pt)
  show heading: set block(above: 2em)
  show heading: it => if capitalize-headings { upper(it) } else { it }

  // Parse user data coming in from the compiler
  let data = json(bytes(sys.inputs.at("data")))

  // document metadata
  set document(title: title, description: data.event_name)

  grid(
    rows: 1fr,
    columns: if stripe-on-outside { (1fr, 4in - 0.75em, 0.75em) } else { (1fr, 0.75em, 4in - 0.75em) },
    // main content area
    grid.cell(x: 0, fill: bg-tint, inset: 2em)[
      #place(left + top)[
        #set image(height: 4em)
        #primary-logo
      ]

      #set align(left + horizon)

      #[
        #show heading: set text(size: 1.75em, fill: title-text-color)
        = #title
      ]

      #set text(fill: accent-color, tracking: if capitalize-headings { 1pt } else { 0pt })
      #show text: it => if capitalize-headings { upper(it) } else { it }

      #let subtitle = if data.challenge == none [ #data.event_name ] else [ Challenge: #data.challenge.name ]

      // as body text, the accent fill and tracking are inherited from above
      #[
        #show heading: set text(..if subtitle-as-heading { (fill: title-text-color, tracking: 0pt) } else { (font: body-font) })
        == #subtitle
      ]

      #datetime(..data.date).display("[month repr:long] [day padding:none], [year]")
    ],
    // accent stripe
    grid.cell(x: if stripe-on-outside { 2 } else { 1 }, fill: accent-color)[],
    // sidebar
    grid.cell(x: if stripe-on-outside { 1 } else { 2 }, fill: sidebar-bg-color, inset: 1.5em)[
      // CISA logo at bottom of sidebar stripe
      #place(right + bottom)[
        #set image(height: 4em)
        #secondary-logo
      ]

      // left align, vertically center contents
      #set align(left + horizon)

      #set text(fill: sidebar-text-color, size: 0.875em)
      #show heading: set text(size: 0.875em)

      == Awarded To
      #data.user_name

      #if data.challenge == none [
        // event cert info
        == Challenges Successfully Attempted
        #let limit = 14 // truncate the challenges list to prevent layout issues.
        #let attempted-challenges = data.challenges_attempted

        #if attempted-challenges.len() == 0 [
          None
        ] else [
          #set list(marker: none, body-indent: 0in)
          #for chal in attempted-challenges.slice(0, calc.min(limit, attempted-challenges.len())) [
            - #chal
          ]
          #if attempted-challenges.len() > limit [
            - #emph[And #(attempted-challenges.len() - limit) more...]
          ]
        ]

        #if data.time_limit_hours != none [
          == Completion Time
          #data.time_limit_hours hours
        ]
      ] else [
        // challenge cert info
        == Challenge Summary
        #data.challenge.summary

        // not including completion time unless we have a good way of computing it
      ]
    ],
  )
}
