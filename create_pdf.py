#!/usr/bin/env python3
"""
Create a pixel-perfect PDF from the CV HTML
Uses Playwright with optimized settings
"""
import asyncio
import sys
from playwright.async_api import async_playwright
import os

async def create_pdf():
    """Generate PDF using Playwright with optimized settings"""

    html_file = os.path.join(os.path.dirname(__file__), 'Cosmin_Turculeanu_PDF_CV.html')
    pdf_file = os.path.join(os.path.dirname(__file__), 'Cosmin T - Resume.pdf')

    print(f"📄 Creating PDF from: {html_file}")
    print(f"💾 Output will be: {pdf_file}")

    async with async_playwright() as p:
        # Launch browser
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

        await browser.close()

        print(f"✅ PDF created successfully: {pdf_file}")
        print(f"📊 File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")

        return pdf_file

if __name__ == "__main__":
    try:
        pdf_path = asyncio.run(create_pdf())
        print(f"\n🎉 Done! Open the PDF with: open '{pdf_path}'")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
