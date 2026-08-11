#import "../_template.typ": certificate-template

// Evergreen certificate applies standard CISA branding to the certificate-template.

#certificate-template(
  body-font: "Franklin Gothic Book",
  display-font: "Franklin Gothic",

  bg-tint: rgb("#005288"),

  primary-logo: image("./logo.png", alt: "President's Cup Cybersecurity Competition"),

  accent-color: rgb("#c0c2c4"),
  stripe-on-outside: true,
  subtitle-as-heading: true
)
