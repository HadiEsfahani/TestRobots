# Complete Website Mapper — GitHub Actions

این پروژه بدون نصب چیزی روی ویندوز، خزنده سایت را روی سرورهای GitHub اجرا می‌کند.

## راه‌اندازی

1. این فایل‌ها را داخل یک Repository در GitHub قرار دهید.
2. وارد تب **Actions** شوید.
3. Workflow با نام **Crawl Website** را انتخاب کنید.
4. روی **Run workflow** بزنید.
5. آدرس سایت را وارد کنید، مثلاً:
   `https://example.com`
6. در صورت نیاز Maximum pages را تغییر دهید.
7. بعد از اتمام، در بخش **Artifacts** فایل `website-map` را دانلود کنید.

## خروجی

- `site-map.csv` — قابل باز کردن با Excel
- `site-map.txt` — تمام URLهای پیدا شده
- `summary.txt` — خلاصه عملیات

## روش کشف صفحات

Crawler ابتدا robots.txt و sitemapها را بررسی می‌کند و سپس لینک‌های داخلی صفحات HTML را دنبال می‌کند. بنابراین فقط به sitemap وابسته نیست.

## نکته

احترام به robots.txt، محدودیت‌های سایت مقصد و شرایط استفاده آن سایت بر عهده کاربر است.
