#!/usr/bin/env python3
"""
Create pixel-perfect PDFs from the CV HTML files (styled + ATS-safe)
Uses Playwright with optimized settings
"""
import asyncio
import sys
from playwright.async_api import async_playwright
import os

TARGETS = [
    {
        'html': 'Cosmin_Turculeanu_PDF_CV.html',
        'pdf': 'Cosmin T - Resume - PM.pdf',
    },
    {
        'html': 'Cosmin_Turculeanu_CV_ATS.html',
        'pdf': 'Cosmin T - Resume - ATS.pdf',
    },
]

async def create_pdf(browser, html_file, pdf_file):
    """Generate a single PDF from an HTML file using an existing browser instance"""

    print(f"📄 Creating PDF from: {html_file}")
    print(f"💾 Output will be: {pdf_file}")

    context = await browser.new_context(
        color_scheme='light',
        viewport={'width': 1200, 'height': 1600}
    )

    page = await context.new_page()

    # Load the HTML file
    print("⏳ Loading HTML...")
    await page.goto(f'file://{html_file}', wait_until='networkidle')

    # Wait for fonts to load
    print("⏳ Waiting for fonts...")
    await page.evaluate('document.fonts.ready')
    await page.wait_for_timeout(2000)

    await page.evaluate('''() => {
        document.querySelectorAll('*').forEach(el => {
            el.style.pageBreakInside = 'auto';
            el.style.pageBreakAfter = 'auto';
            el.style.pageBreakBefore = 'auto';
        });
    }''')

    print("⏳ Generating PDF...")
    await page.pdf(
        path=pdf_file,
        format='A4',
        print_background=True,
        display_header_footer=False,
        margin={
            'top': '0',
            'right': '0',
            'bottom': '0',
            'left': '0'
        }
    )

    await context.close()

    print(f"✅ PDF created successfully: {pdf_file}")
    print(f"📊 File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")


async def create_all_pdfs():
    """Generate PDFs for every target HTML file"""

    base_dir = os.path.dirname(__file__)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/Users/cosmint/Library/Caches/ms-playwright/chromium_headless_shell-1169/chrome-mac/headless_shell",
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--force-color-profile=srgb',
                '--disable-dev-shm-usage'
            ]
        )

        pdf_paths = []
        for target in TARGETS:
            html_file = os.path.join(base_dir, target['html'])
            pdf_file = os.path.join(base_dir, target['pdf'])

            if not os.path.exists(html_file):
                print(f"⚠️  Skipping missing file: {html_file}", file=sys.stderr)
                continue

            await create_pdf(browser, html_file, pdf_file)
            pdf_paths.append(pdf_file)
            print()

        await browser.close()

        return pdf_paths

if __name__ == "__main__":
    try:
        pdf_paths = asyncio.run(create_all_pdfs())
        print(f"\n🎉 Done! Generated {len(pdf_paths)} PDF(s):")
        for path in pdf_paths:
            print(f"   open '{path}'")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
