# Civil Career Portal

GitHub Pages career monitor for Taiwan and Singapore civil-engineering academic and research opportunities, tailored to green cement, sustainable concrete, additive manufacturing and smart cementitious materials.

## Publish once
1. Create a **public** repository named `civil-career-portal` without README or starter files.
2. Upload all files and folders from this package to the repository root.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`.
5. Open **Actions → Update career opportunities → Run workflow** once.

Your site URL will be `https://YOUR-USERNAME.github.io/civil-career-portal/`.

## Automatic updates
The workflow runs daily at 08:15 Asia/Taipei. It checks the official source pages in `sources.json`, adds matching candidate links to `data/jobs.json`, and marks automatically discovered items as **Review Needed**. This is deliberate: institutional recruitment systems and page layouts change, and no generic scraper can guarantee that every candidate is a valid open vacancy.

To add a new official institution, edit `sources.json`. Favorites remain in each visitor's browser local storage.
