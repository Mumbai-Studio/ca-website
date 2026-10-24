# Collaborative Architecture website · guide for the host

**For:** the developer or host who puts collaborativearchitecture.com online.
**Version:** 25 October 2026.

**In short:** the new site is a set of ready-made files: a static site plus two small PHP scripts for the forms.

- There is no WordPress and no database.
- There is nothing to install or compile on the server.
- You upload the folder, add one settings file for the forms, test it, then point the domain at it.

---

## 1. What you are getting

| In the package | What it is |
|---|---|
| `site/` | **The website. Upload the contents of this folder to the web root.** It holds: 65 pages, each as its own `index.html` (`/`, `/work/`, `/work/wedge-1/` …); `404.html`; pictures (`img/`), films (`vid/`), fonts (`fonts/`) and scripts (`assets/`); the search files (`sitemap.xml`, `robots.txt`, `llms.txt`, feeds); and the server settings (`.htaccess`, `_redirects`, `_headers`). |
| `site/api/` | The two form handlers: `contact.php` (the inquiry form) and `subscribe.php` (the newsletter). `config.sample.php` is the settings template, and `lib.php` is shared code. |
| `site/site-config.js` | The settings you can change without a new build: Google Analytics ID, Turnstile key, form addresses. |
| `server/nginx.conf` | The same server rules for nginx, if the server is not Apache or LiteSpeed. |
| `docs/HOST-GUIDE.md` | This guide. |

The same files live in the studio's private GitHub repository, `Mumbai-Studio/ca-website`. Ask the studio to invite you.

- The ready-to-serve copy is on the **`live-site`** branch.
- The source and build tools are on **`main`**.

## 2. What the server needs

- **Web server:** any server that serves files over HTTPS.
  - Best: **Apache or LiteSpeed with `.htaccess` enabled** (`AllowOverride All`, `mod_rewrite`, `mod_headers`). Most cPanel hosting is like this.
  - nginx works with `server/nginx.conf`.
  - Netlify and Cloudflare Pages also work, using `_redirects` and `_headers`, but they have no PHP: see 5.4.
- **PHP 7.4 or later, for the two form handlers.** PHP 8.2 or 8.3 is recommended. It needs the `curl` or `openssl` extension, which is standard.
- **About 140 MB of disk space.**
- **The site must sit at the root of a domain or subdomain,** for example `collaborativearchitecture.com/` or `new.collaborativearchitecture.com/`.
  - It cannot run from a subfolder such as `example.com/new/`, because every link starts with `/`.

## 3. Before you start: keep the old site

The current site is WordPress.

1. **Back it up in full** (files and database) and keep the backup for at least three months. This is the way back if anything goes wrong (see 10).
2. Do not delete WordPress until the new site has been live for a few weeks.
   - If the new site goes into the same web root, move WordPress into a folder outside the web root, or keep it as a cPanel backup.

## 4. Upload

### 4.1 cPanel, Apache or LiteSpeed (most likely)

1. **Upload the contents of `site/` into the web root** of the account the domain will point to (usually `public_html/`).
   - Upload the *contents* of `site/`, not the `site` folder itself.
   - The easiest way is to upload `site.zip` in cPanel's File Manager and choose *Extract*.
2. **Check that the hidden file `.htaccess` arrived.** In File Manager, open *Settings → Show hidden files*. This file holds every redirect and security rule; without it the old addresses break.
3. **Check permissions:** folders 755, files 644. These are the normal defaults.
4. **Set PHP 8.x** for the domain (cPanel → *MultiPHP Manager*).
5. **Finish the form settings** (section 5).

### 4.2 nginx (a VPS)

1. Copy the contents of `site/` to `/var/www/collaborativearchitecture.com/`.
2. Use `server/nginx.conf`. Set `root`, the certificate lines and the `fastcgi_pass` socket for your PHP-FPM.
3. Then run `nginx -t && systemctl reload nginx`.

### 4.3 Netlify or Cloudflare Pages

1. Connect the GitHub repository, choose branch **`live-site`**, leave the build command empty, and set the publish folder to `/`.
2. `_redirects` and `_headers` apply automatically.
3. These hosts do not run PHP; see 5.4 for the forms.

## 5. The forms

The inquiry form and the newsletter post to `/api/contact.php` and `/api/subscribe.php`.

Inquiries are routed by type:

| Type of inquiry | Goes to |
|---|---|
| Client, Consultants, Research | enquiry@collaborativearchitecture.com |
| Career | studio@collaborativearchitecture.com |
| Vendors | vendors@collaborativearchitecture.com |

Every message is also kept as a copy in `/_private/` (one file a month). Web access to that folder is refused.

### 5.1 Settings file (needed)

1. In `api/`, **copy `config.sample.php` to `config.php`** and fill it in.
   - `config.php` holds passwords. It stays on the server only and is never put in the repository.
   - Automatic deployments never overwrite it.
2. Set `from_email`: the address the site's emails come from. Create `website@collaborativearchitecture.com` in Google Workspace, as a user or an alias.
3. **SMTP (strongly recommended).** Send through Google Workspace so the emails are authenticated and do not land in spam:
   1. Sign in to Google as the `from_email` account.
   2. Turn on 2-Step Verification.
   3. Create an app password at myaccount.google.com/apppasswords.
   4. Put it in `smtp.pass`. Keep `smtp.gmail.com`, port 465, `ssl`.
4. If you leave `smtp.host` empty, PHP's own `mail()` is used. That only delivers well if the server's IP is in the domain's SPF record (see 7.3).

### 5.2 Security check (optional)

The forms already refuse automated messages: a hidden field, a minimum time on the page, and a limit per connection.

For stronger protection:

1. Create a free **Cloudflare Turnstile** widget for the domain.
2. Put the *site key* in `site-config.js` (`turnstileSiteKey`).
3. Put the *secret key* in `config.php` (`turnstile_secret`).

### 5.3 Newsletter

- **Without Mailchimp settings:** each sign-up is emailed to `newsletter_to` and kept in `_private/newsletter/`, to be added to Mailchimp by hand.
- **With Mailchimp** (an API key and the audience ID in `config.php`): addresses join the audience directly, and Mailchimp sends the confirmation email (double opt-in).

### 5.4 Hosts without PHP

On Netlify or Cloudflare Pages:

1. Use a form service such as Formspree or Web3Forms.
2. Put its address in `site-config.js` (`contactEndpoint`, `subscribeEndpoint`).

The forms send ordinary `FormData` fields: `name`, `organization`, `email`, `telephone`, `country`, `inquiry_type`, `portfolio`, `message`, `studio`.

### 5.5 Test the forms

1. Send one inquiry of each type, and check that each arrives in the right mailbox.
2. Subscribe once.
3. Open `/_private/` and `/api/config.php` in a browser: both must answer **403**.

## 6. Test before the domain moves

The surest test is to see the new server under the real name while the public still sees the old site:

1. **Edit your own computer's `hosts` file** to point `collaborativearchitecture.com` and `www.collaborativearchitecture.com` at the new server's IP.
2. A temporary certificate warning is normal until SSL is issued (see 8).

A subdomain such as `new.collaborativearchitecture.com` also works. If you use one, protect it with a password (cPanel → *Directory Privacy*) so search engines do not index the copy.

**Checks:**

- [ ] `/` opens: the opening animation, then the home page. On a phone too.
- [ ] Work, a few project pages, Expertise, Lab, Awards, Studio, News, Contact, Privacy, Cookies.
- [ ] Menu, search, image viewer, a project film (Cascadia, National Unity Pavilion), the map view (Work → Map).
- [ ] The cookie box appears once; *Accept all* and *Essential only* both close it.
- [ ] The inquiry and newsletter forms (5.5).
- [ ] An unknown address such as `/abc/` shows *Page not found*, with status 404.
- [ ] **Old addresses redirect.** For example:
  - `/portfolio-item/wedge-1/` → `/work/wedge-1/`
  - `/portfolio-item/herman-miller-experience-center/` → `/work/miller-knoll-experience-center/`
  - `/publications/` → `/news/press/`
  - `/about/` → `/studio/`
  - `/wp-admin/` answers 410 (gone)
- [ ] `https://www.…` and `http://…` both redirect to `https://collaborativearchitecture.com/…`.
- [ ] **Headers:** `curl -I https://collaborativearchitecture.com/` shows `Content-Security-Policy`, `Strict-Transport-Security` and `X-Content-Type-Options`.

## 7. Move the domain (DNS)

**If the new site goes on the same server and account as the current WordPress site,** there is no DNS change: replace the files in the web root (after the backup) and go to step 8.

Otherwise, follow 7.1 to 7.3.

### 7.1 Where the DNS is

The domain's DNS is served by the registrar's name servers: `chrisansweb.earth / .mars / .venus.orderbox-dns.com`. That is a ResellerClub (LogicBoxes) reseller panel, so the studio needs that login.

### 7.2 What to change, and what never to change

1. **A day before:** lower the TTL of the `@` and `www` records to 300 seconds.
2. **On the day:**
   1. Change the **A record of `@`** to the new server's IP.
   2. Point **`www`** at the same IP (A record) or at `@` (CNAME).
   3. If the server has an IPv6 address, add an AAAA record too.
3. **Do not touch** the records that run the studio's email:

   | Record | Value |
   |---|---|
   | MX (priority 1) | `aspmx.l.google.com` |
   | MX (priority 5) | `alt1.aspmx.l.google.com` |
   | MX (priority 5) | `alt2.aspmx.l.google.com` |
   | MX (priority 10) | `aspmx2.googlemail.com` to `aspmx5.googlemail.com` |
   | TXT | the `MS=…` verification |

   Take a screenshot of the whole DNS zone before changing anything.

### 7.3 Email authentication (missing today, add it now)

The domain has **no SPF and no DMARC record** today. Gmail and Yahoo now expect both, so the studio's own emails can land in spam without them.

1. **SPF:** a TXT record on `@`: `v=spf1 include:_spf.google.com ~all`.
   - If the web server sends with `mail()` instead of SMTP, add its IP: `v=spf1 ip4:SERVER_IP include:_spf.google.com ~all`.
   - There must be only one SPF record.
2. **DKIM:**
   1. In Google Admin → Apps → Google Workspace → Gmail → *Authenticate email*, generate the key.
   2. Add it as the TXT record `google._domainkey`.
   3. Then press *Start authentication*.
3. **DMARC:** a TXT record on `_dmarc`: `v=DMARC1; p=none; rua=mailto:enquiry@collaborativearchitecture.com`.
   - After a month of clean reports, move to `p=quarantine`.

## 8. HTTPS

- Issue certificates for **both** `collaborativearchitecture.com` and `www.collaborativearchitecture.com`: cPanel *AutoSSL*, Let's Encrypt, or the host's own.
- Once both work, `.htaccess` sends every visitor to `https://collaborativearchitecture.com/` without www.
  - That redirect applies only on the real domain, so a test address still works over plain http.
- The site sends `Strict-Transport-Security` (one year). Enable HTTPS before going live, not after.

## 9. After launch

**On the day:**

- [ ] Repeat the checks in 6 on the real address, from a phone on mobile data as well.
- [ ] **Google Search Console:**
  1. Add a *Domain* property and verify it with the DNS TXT record Google gives.
  2. Submit `https://collaborativearchitecture.com/sitemap.xml`.
  3. Ask for indexing of the home page.
- [ ] **Bing Webmaster Tools:** import the site from Search Console, then submit the sitemap. The IndexNow key file is already published.
- [ ] **Google Analytics 4:**
  1. Create the property.
  2. Put the measurement ID (`G-…`) in `site-config.js`.
  3. Set data retention to 14 months, as the privacy page says.
  - Analytics load only after a visitor accepts them in the cookie box.

**In the first two weeks:**

- [ ] Watch the server's 404 log and Search Console's *Pages* report. Any old address that still matters gets a line in `server/redirects.txt`; the next build adds it to `.htaccess`.
- [ ] Check Core Web Vitals in Search Console after about 28 days.

## 10. If something goes wrong (rollback)

- **Same server:** put the WordPress backup back in the web root.
- **New server:** point the A records back to the old IP. With the TTL at 300 seconds, that takes effect within minutes.

Email is unaffected either way, as long as the MX records were left alone.

## 11. Changing the site later

- **Do not edit the HTML files on the server.** They are generated, and the next deployment replaces them.
- The source is `src/ca-website.html` in the repository; pictures are in `public/img/`. The studio requests changes through Claude, which edits the repository.
- **Automatic deployment (recommended):** every change pushed to `main` is built, checked and uploaded by GitHub Actions (`.github/workflows/deploy.yml`). To switch it on, in the repository's *Settings → Secrets and variables → Actions*:
  - **FTP (cPanel):**
    - Secrets: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`. Create an FTP account limited to the web root.
    - Variables: `DEPLOY` = `ftp`, and `FTP_DIR` (for example `public_html/`).
  - **SSH (VPS):**
    - Secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`.
    - Variables: `DEPLOY` = `ssh`, and `SSH_DIR`.
  - **cPanel Git Version Control instead:** clone the `live-site` branch into the web root and pull after each change.
- **By hand:** download the latest built site (the run's *site* download on GitHub, or the `live-site` branch as a ZIP) and upload it over the old files. Keep `api/config.php` and `_private/`.

## 12. Where to ask

- **Website content and decisions:** Mujib Ahmed (studio).
- **Domain and registrar login:** the studio, through the ChrisAnsWeb / ResellerClub panel.
- **Email (Google Workspace admin):** the studio's Workspace administrator.
