Collaborative Architecture website, patch 2026-11-27-mail1: the website's emails delivered through Google

Why: the Contact form and the newsletter sign-ups are handed to the web server's own mail program, and none of them reaches the
studio's Google mailboxes. The domain's mail is with Google Workspace, it has no SPF record, and a cPanel server keeps mail for
its own domain in local mailboxes. From this patch on every form email goes out through Google with an app password.

Files: five, all in api/. Nothing outside api/ changes; no page, script, style or picture. Upload it together with patch
2026-11-27-newsletter1 (which holds press@'s app password, used here too). Independent of patch 2026-11-26-gsc1.

1. Upload the files in upload/api/ to the site's api/ folder (for example public_html/api/), overwriting:
     api/lib.php          (the forms' shared code: sending through Google)
     api/subscribe.php    (the newsletter sign-up)
     api/mail-check.php   (a check page, see step 5)
     api/mail.php         (settings: optional app passwords per mailbox, and the key of the check page)
     api/.htaccess        the file htaccess.txt, RENAMED to .htaccess (a hidden file: in cPanel's File Manager turn on
                          Settings > Show hidden files). It now also closes mail.php to the web.
   Do not change api/config.php or the _private/ folder.

2. cPanel > Email > Email Routing: for collaborativearchitecture.com choose "Remote Mail Exchanger" and save. Then mail that the
   server sends to @collaborativearchitecture.com goes to Google, not to local mailboxes on the server.

3. Mail that never arrived: inquiries and sign-ups since launch were not lost on the server.
   a) The forms keep a copy of every message in _private/inquiries/ and _private/newsletter/ (one .jsonl file per month).
      Send those files privately to the studio (they hold visitors' names and emails).
   b) If cPanel > Email Accounts lists mailboxes such as enquiry@, studio@, vendors@, newsletter@ or press@ on this server,
      open them in webmail, forward their messages to the studio, and tell the studio before deleting those local mailboxes.

4. nginx servers only: in nginx.conf add mail and mail\.sample to the denied list and mail-check to the PHP list:
     location ~ ^/api/(lib|config|config\.sample|mailchimp|mailchimp\.sample|security|security\.sample|mail|mail\.sample)\.php$ { deny all; }
     location ~ ^/api/(contact|subscribe|vitals|mail-check)\.php$ { ... as before ... }
   then run  nginx -t && systemctl reload nginx

5. Check (the studio has the key for the check page, which is in api/mail.php as check_key):
   - https://collaborativearchitecture.com/api/mail.php answers 403 (Forbidden).
   - https://collaborativearchitecture.com/api/mail-check.php?key=KEY&send=all
     shows how each form's email leaves the server ("Google (smtp.gmail.com) as press@..." or as the mailbox itself) and sends
     one short test email to enquiry@, studio@, vendors@ and newsletter@. Each line must read "handed to the mail server".
     "cannot connect to smtp.gmail.com" means the server blocks outgoing mail ports: allow outgoing connections to
     smtp.gmail.com on ports 465 and 587 (WHM > Security Center > SMTP Restrictions, or the firewall's SMTP_BLOCK setting).
     "AUTH ... answered 535" means an app password is wrong: tell the studio which mailbox.
   - Send one test inquiry from https://collaborativearchitecture.com/contact/ in a normal browser; the studio confirms it arrived.

6. Reply to the studio that patch 2026-11-27-mail1 is on the server, with the result of the check page.
