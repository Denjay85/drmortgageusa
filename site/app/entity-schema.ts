const origin = "https://drmortgageusa.com";

export const dennisRossId = `${origin}/about#dennis-ross`;
export const drMortgageOrganizationId = `${origin}/#organization`;
export const websiteId = `${origin}/#website`;
export const home1stOrganizationId = "https://myhome1st.com/#organization";

export const dennisRossSameAs = [
  "https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381",
  "https://myhome1st.com/dennis/",
  "https://www.google.com/maps?cid=3829412552217676351",
  "https://www.instagram.com/dr.mortgageusa/",
  "https://www.facebook.com/p/Dennis-Ross-Mortgage-Loan-Originator-Nmls2018381-100084710485166/",
  "https://www.linkedin.com/in/dennis-ross-87491257",
  "https://www.youtube.com/@Dr.MortgageUSA",
];

export const home1stOrganizationSchema = {
  "@type": "Organization",
  "@id": home1stOrganizationId,
  name: "Home 1st Lending, LLC",
  url: "https://myhome1st.com/",
  identifier: {
    "@type": "PropertyValue",
    propertyID: "NMLS",
    value: "1418",
  },
  address: {
    "@type": "PostalAddress",
    streetAddress: "1130 Business Center Dr, Suite 1000",
    addressLocality: "Lake Mary",
    addressRegion: "FL",
    postalCode: "32746",
    addressCountry: "US",
  },
};

export const dennisRossSchema = {
  "@type": "Person",
  "@id": dennisRossId,
  name: "Dennis Ross",
  alternateName: ["DR. Mortgage USA", "DrMortgageUSA"],
  url: `${origin}/about`,
  image: `${origin}/media/dennis.webp`,
  description:
    "Known publicly as DR. Mortgage USA, Dennis Ross is a Navy veteran and Florida Mortgage Loan Originator with Home 1st Lending, LLC, helping Greater Orlando veterans, buyers, and homeowners understand their financing options.",
  disambiguatingDescription:
    "Dennis Ross, individual NMLS 2018381, is the Navy veteran behind the DR. Mortgage USA professional brand and website. He is based in Lake Mary, serves Greater Orlando, and originates mortgage loans through Home 1st Lending, LLC, company NMLS 1418.",
  jobTitle: "Mortgage Loan Originator and Mortgage Broker",
  telephone: "+1-850-346-8514",
  email: "dennis@drmortgageusa.com",
  identifier: {
    "@type": "PropertyValue",
    propertyID: "NMLS",
    value: "2018381",
  },
  worksFor: { "@id": home1stOrganizationId },
  sameAs: dennisRossSameAs,
  knowsAbout: [
    "VA home loans in Greater Orlando",
    "Florida mortgages",
    "VA loan entitlement and funding fees",
    "FHA loans",
    "Down payment assistance",
    "Self-employed mortgage lending",
    "Home equity financing",
    "Mortgage planning for first-time homebuyers",
  ],
};

export const drMortgageOrganizationSchema = {
  "@type": "FinancialService",
  "@id": drMortgageOrganizationId,
  name: "DR. Mortgage USA",
  alternateName: [
    "DR. Mortgage USA",
    "DrMortgageUSA",
    "Dennis Ross, Dr.MortgageUSA",
    "Dennis Ross Mortgage Broker",
  ],
  url: `${origin}/`,
  description:
    "DR. Mortgage USA is the professional brand and educational website of Navy veteran Dennis Ross, individual NMLS 2018381, serving Greater Orlando and Florida through Home 1st Lending, LLC, company NMLS 1418. It is not a separate lender or mortgage company.",
  disambiguatingDescription:
    "The DR. Mortgage USA name on drmortgageusa.com identifies Dennis Ross and his Greater Orlando mortgage practice through Home 1st Lending, LLC; it does not identify Dr. Mortgage, LLC or another separately licensed mortgage company.",
  logo: {
    "@type": "ImageObject",
    url: `${origin}/media/logo.webp`,
    contentUrl: `${origin}/media/logo.webp`,
    width: 192,
    height: 158,
  },
  image: `${origin}/media/dennis.webp`,
  telephone: "+1-850-346-8514",
  email: "dennis@drmortgageusa.com",
  address: {
    "@type": "PostalAddress",
    streetAddress: "1130 Business Center Dr, Suite 1000",
    addressLocality: "Lake Mary",
    addressRegion: "FL",
    postalCode: "32746",
    addressCountry: "US",
  },
  geo: {
    "@type": "GeoCoordinates",
    latitude: 28.7842131,
    longitude: -81.3610467,
  },
  openingHoursSpecification: [
    {
      "@type": "OpeningHoursSpecification",
      dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      opens: "09:00",
      closes: "19:00",
    },
    {
      "@type": "OpeningHoursSpecification",
      dayOfWeek: "Saturday",
      opens: "11:00",
      closes: "17:00",
    },
  ],
  areaServed: [
    { "@type": "City", name: "Orlando" },
    { "@type": "City", name: "Lake Mary" },
    { "@type": "AdministrativeArea", name: "Central Florida" },
    { "@type": "State", name: "Florida" },
  ],
  founder: { "@id": dennisRossId },
  parentOrganization: { "@id": home1stOrganizationId },
  sameAs: dennisRossSameAs,
  knowsAbout: dennisRossSchema.knowsAbout,
};

export const websiteSchema = {
  "@type": "WebSite",
  "@id": websiteId,
  name: "DR. Mortgage USA",
  alternateName: "DrMortgageUSA",
  url: `${origin}/`,
  publisher: { "@id": drMortgageOrganizationId },
  inLanguage: "en-US",
};

export const homepageEntitySchema = {
  "@context": "https://schema.org",
  "@graph": [
    drMortgageOrganizationSchema,
    dennisRossSchema,
    home1stOrganizationSchema,
    websiteSchema,
  ],
};

export const dennisProfilePageSchema = {
  "@context": "https://schema.org",
  "@type": "ProfilePage",
  "@id": `${origin}/about#profile-page`,
  url: `${origin}/about`,
  name: "Dennis Ross, NMLS 2018381 | Greater Orlando VA Home Loan Guidance",
  description:
    "Professional profile for Dennis Ross, Navy veteran and Greater Orlando mortgage broker, NMLS 2018381.",
  mainEntity: dennisRossSchema,
  isPartOf: { "@id": websiteId },
};
