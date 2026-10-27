/* Collaborative Architecture · site settings
   The only file on the server that can be changed without a new build. Leave a value empty ('') to switch that feature off.
   After a change, upload this one file; visitors get it within the hour. */
window.CA_CONFIG = {
  // Google Analytics 4 measurement ID, for example 'G-AB12CD34EF'. Analytics load only after a visitor accepts them.
  ga4: '',

  // Cloudflare Turnstile site key (the public one), for the security check on the inquiry and newsletter forms.
  // Leave empty to rely on the form handler's own checks; the secret key goes in api/config.php.
  turnstileSiteKey: '',

  // Where the forms send. The defaults are the PHP handlers in /api/. On a host without PHP, use a form service's address.
  contactEndpoint: '/api/contact.php',
  subscribeEndpoint: '/api/subscribe.php',

  // The address of the newsletter's past editions (the Mailchimp campaign archive), shown on the Lab page when filled in.
  newsletterArchive: '',

  // Search engine verification codes, if the meta-tag method is used. They are written into the pages at the next build;
  // the DNS method (a TXT record) needs nothing here and is the one recommended.
  googleVerify: '',
  bingVerify: '',

  // false only on a staging copy: every page then asks search engines not to index it.
  indexable: true
};
