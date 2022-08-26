# Frugality v 0.1 - WIP

Current iteration of the groceries price calculator.

Changes: Data is collected directly via an API. (Websites without one will still use the webscraper for this task)
The webscraper module is currently not functional/being used as I was in the middle of an overhaul when the target website changed domains (and it's overall structure) :(. This has been left in though, as scraping other competitor websites may still require it in the future.

"active" branch shows current progress

Basic project idea/vision:
- Grocery bag price calulcator
- Scope of the project is limited to the larger grocery store chains situated in Finland
- Able to compare competitors store prices for entire grocery lists / individual recipes / individual items
- Able to utilize google maps api to search nearby stores by utilizing a given street address (user defined radius)
- Able to factor in transit cost into final calculation
- Able to factor in potential delivery cost into final calculation

Distant future:
- Price history and statistics
- Desktop and/or mobile app?
- Able to scan in receipts through a mobile app
- Would facilitate the ability to keep track of items already in fridge
- Would also mean that the project would change in nature towards a general expenditure tracker
