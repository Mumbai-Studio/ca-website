# Patch 2026-11-27-mail1: the website's emails delivered through Google

## Found (27 November 2026)

- A test inquiry (Client) sent to the live api/contact.php was answered `{"ok":true}` in about half a second, and nothing arrived
  in enquiry@; no website inquiry arrived there in the last 30 days (checked in the enquiry@ mailbox).
- DNS: MX is Google Workspace; there is no SPF record and no Google DKIM record; DMARC p=none; Mailchimp's k2/k3 CNAMEs exist.
- The server hands mail to its own mail program (PHP mail()). A cPanel server keeps mail for its own domain locally unless
  Email Routing is set to Remote, and without SPF Google treats mail from the server as unauthenticated.

## Changes (public/api, brought in line with the live 21 Nov files first)

- lib.php: every form email goes out through Google (smtp.gmail.com, 465, or 587 with STARTTLS when 465 is closed) with an app
  password: the receiving mailbox's own (api/mail.php, optional) or the fallback account, press@ with the app password from
  mailchimp.php. A mailbox whose own password fails sends through the fallback. Error texts never include a credential.
  The newsletter keeps its own sender (newsletter@ through press@) and never uses config.php's server.
- subscribe.php: press@'s app password without spaces, and the same Google host setting.
- mail-check.php: a key-protected page that reports the settings (Cloudflare secret accepted, Mailchimp key and audience, the
  route of each mailbox) and sends test emails on request; no passwords in its output.
- mail.sample.php, and .htaccess closes mail.php to the web.

## Tests (PHP 8.3 built-in server, a local SMTP server with a test certificate standing in for Google: tools/patches/mail1/fakesmtp.py)

- Client, Career, Vendors reach enquiry@, studio@, vendors@ through press@, From "Collaborative Architecture website", Reply-To
  the visitor; an app password pasted with spaces works.
- A mailbox's own password: sent as that mailbox. A wrong one: retried through press@, delivered, the reason logged.
- Port 465 closed: delivered on 587 with STARTTLS.
- Newsletter notice: to newsletter@ through press@, as newsletter@.
- Nothing filled in: the route reads "the web server's own mail()", as today.
- mail-check: 404 without the key; settings and routes; send=all reports each mailbox, with the 535 text for a wrong password;
  no password or its base64 form in the output or the log. Apache: api/mail.php, mailchimp.php, security.php answer 403.
