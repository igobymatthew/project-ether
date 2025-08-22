from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        page.goto("http://localhost:8080/index.html")

        page.wait_for_load_state("networkidle")

        # Click the "Dial" button
        dial_button = page.locator("#dial")
        dial_button.click()

        # Wait for the call to connect by checking the log
        expect(page.locator("#log")).to_contain_text("[ws-audio] connected", timeout=10000)

        # Take a screenshot
        page.screenshot(path="jules-scratch/verification/verification.png")

        # Check for audio element
        audio_element = page.locator("audio")
        expect(audio_element).to_be_visible()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
