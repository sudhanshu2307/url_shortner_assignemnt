URL Shortener Service - A Quick Peek Under the Hood
Hey there! This document gives you a friendly rundown of how I put together the URL Shortener Service. Think of it as a little chat about the project's ins and outs.

1. What It Does (Core Features):
Making URLs Shorter (POST /api/shorten):

You send it a long URL, and it gives you back a neat, short 6-character code (like "abc123").

It's smart enough to check if your URL is valid before doing anything.

If you try to shorten the same long URL again, it'll just hand you back the existing short code – no need for duplicates!

All these short codes and their original URLs are tucked away for later.

Sending You Where You Need to Go (GET /<short_code>):

When someone clicks on one of those short codes, this part springs into action, redirecting them straight to the original long URL.

If a short code doesn't exist, it'll politely tell you it can't find it (a "404 Not Found" error).

Oh, and every time someone uses a short link, it quietly adds one to the click count – pretty cool for tracking!

Spilling the Beans on Stats (GET /api/stats/<short_code>):

Want to know how popular your short link is? Just ask this endpoint!

It'll tell you the original URL, how many times it's been clicked, and when it was first created.

Again, if the short code isn't found, it'll let you know with a 404.

2. How It's Built (Behind the Scenes):
Where the Data Lives: For this project, I kept things simple and used a basic Python dictionary (url_store) right in the app's memory to hold all the URL mappings. This keeps us away from needing a big, fancy database, just like the assignment asked!

Keeping Things Smooth (Concurrency): When lots of people try to shorten or access URLs at the same time, things can get messy. So, I added a threading.Lock (store_lock) to make sure everything happens in an orderly fashion, preventing any mix-ups.

Crafting Short Codes: Those 6-character codes are randomly generated using Python's random and string modules. I made sure each one is totally unique before it's given out.

Checking URLs: Before shortening, I've got a little check in place using urllib.parse.urlparse to make sure the URL you provide is actually a proper web address.

Handling Oopsies: If something goes wrong (like a bad URL or a missing short code), the app is designed to give clear HTTP error messages (like a 400 for a bad request or a 404 for something not found).

3. Making Sure It Works (Testing):
I've set up a bunch of automated tests in tests/test.py using pytest.

These tests cover all the main features, plus they check for common mistakes or edge cases (like invalid input or trying to find a link that doesn't exist).

Each test starts fresh, so the url_store is always clean, ensuring reliable results.

4. A Note on AI Assistance:
Tool Used: Gemini (Google's Large Language Model).

How it Helped: It was a handy assistant for getting the initial project structure and boilerplate code set up. It also offered some pointers on Python syntax and common Flask patterns. When I hit a snag with environment setup (like tricky PowerShell commands or virtual environment activation) or needed to fine-tune my test logic, it provided useful suggestions.

My Contribution: I made sure to review and adapt any suggestions to fit the project's overall design, and I did all the hands-on coding and problem-solving myself. Any AI-generated snippets were minor and integrated carefully.