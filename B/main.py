from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import json
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Flight Search API")



@app.get("/search-flights")
def search_flights(
    origin: str = Query(..., description="Origin city, e.g. Bangalore"),
    destination: str = Query(..., description="Destination city, e.g. Delhi"),
    journey_date: str = Query(..., description="Journey date in YYYY-MM-DD format")
):
    with sync_playwright() as p:
        origin="Bangalore"
        destination="Delhi"
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()

        # Open BudgetTicket website
        page.goto("https://www.budgetticket.in/", wait_until="domcontentloaded")

        # -------- Origin: Bangalore --------
        from_input = 'input[placeholder*="Select Origin City"]'
        page.click(from_input)
        page.fill(from_input, "")  # clear any existing value

        for char in "Bangalore":
            page.keyboard.type(char, delay=150)  # type slowly
        page.wait_for_timeout(1000)  # wait for dropdown

        page.keyboard.press("Enter")

        # -------- Destination: Delhi --------
        to_input = 'input[placeholder*="Select Destination City"]'
        page.fill(to_input, "")  # clear any existing value

        for char in "Delhi":
            page.keyboard.type(char, delay=150)  # type slowly
        page.wait_for_timeout(1000)  # wait for dropdown

        page.keyboard.press("Enter")

        

        # -------- Journey Date (7 days from now) --------
        journey_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        date_input = 'input[placeholder*="Depart"], input[aria-label*="Depart"], input[name*="date"]'
        page.click('.datepicker.search-date.open_sans_fonts.mb-0.pointer.underline.ng-binding')
        page.wait_for_timeout(1000)
        page.mouse.click(900, 450)



        # -------- Click Search Flights --------
        page.click('button:has-text("Search"), input[value*="Search"], [aria-label*="Search"]')

        # -------- Wait for results to load --------
        page.wait_for_load_state("networkidle")

        print("✅ Flight search completed — results loaded successfully.")

        # After search: extract results
        page.wait_for_selector(".card-body", state="attached", timeout=15000)  # safer: just attached
        cards = page.query_selector_all(".card-body")
        print(f"got {len(cards)} card body elements")

        results = []
        for card in cards:
            try:
                full_text = card.inner_text().strip()
                lines = [line.strip() for line in full_text.splitlines() if line.strip()]
                # Robust index checks
                airline = lines[0] if len(lines) > 0 else ""
                flight_number = lines[1] if len(lines) > 1 else ""
                if airline =="" or flight_number == "":
                    continue  # skip incomplete entries

                # Departure and arrival: use first match for BLR, last for DEL (safer if code share/etc.)
                dep_index = next((i for i, l in enumerate(lines) if l.endswith("BLR") or l.endswith("BANGALORE")), None)
                departure_time = lines[dep_index + 1].split()[0] if dep_index is not None and (dep_index + 1) < len(lines) else ""
                arr_index = next((i for i, l in reversed(list(enumerate(lines))) if l.endswith("DEL") or l.endswith("DELHI")), None)
                arrival_time = lines[arr_index + 1].split()[0] if arr_index is not None and (arr_index + 1) < len(lines) else ""

                # Find ₹ for price, get only digits and ₹
                price_line = next((l for l in lines if "₹" in l), "")
                price = ''.join(c for c in price_line if c.isdigit() or c == "₹") if price_line else ""

                results.append({
                    "airline": airline,
                    "flight_number": flight_number,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "orgin": origin,
                    "destination": destination,
                    "price": price[:-2]+"."+price[-2:]
                })
            except Exception as e:
                print(f"Error parsing flight card: {e}")
                continue

        with open("flight_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Extracted {len(results)} flight results.")
        browser.close()
        return JSONResponse(content={"results": results})
    

# if __name__ == "__main__":
#     search_flights()
