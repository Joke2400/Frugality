# Frugality

A webapp to help you find the cheapest groceries nearby.

WIP, host over the internet at your own risk. 
Current scope limited to S-Ryhmä-owned stores.
Other stores will also be included once I get to it.

Note:
I will begin migrating this to FastAPI & PostgresSQL. The frontend may also be rebuilt aswell. This might lead to the latest dev branch being a bit funky at times.

Basic project idea/vision:
- Groceries price calulcator.
- Simple, unbiased & quick to use.
- Able to compare competitors store prices for entire grocery lists / individual recipes / individual items.
- Able to utilize google maps api to search nearby stores by utilizing a given street address (user defined radius).
- Able to factor in transit cost into final calculation.
- Able to factor in potential delivery cost into final calculation.
- Caching of previously fetched price data for price development statistics.

Docker:
- Docker config is configured to be used in conjuction with Vscode's Dev Containers extension.