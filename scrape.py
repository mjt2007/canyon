from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
def scrape_canyon_bikes(url):

    # Fetch the webpage
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch URL: {response.status_code}")
        return
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all bikes (each bike is wrapped in `productTileDefault`)
    # bike_tiles = soup.find_all('div', class_='productTileDefault__productSummary')
    bike_tiles = soup.find_all('div', class_=re.compile(r'productTileDefault--bike', re.I))
    results = []
    for bike_tile in bike_tiles:
        # Extract bike name
        name_tag = bike_tile.find('a', class_='productTileDefault__productName')
        name = name_tag.text.strip() if name_tag else "N/A"
        # Extract sale price
        sale_price_tag = bike_tile.find('div', class_='productTile__priceSale')
        sale_price = sale_price_tag.text.strip().replace("$", "").replace(",", "") if sale_price_tag else "N/A"
        # Extract original price
        original_price_tag = bike_tile.find('s', class_='productTile__priceOriginal')
        original_price = original_price_tag.text.strip().replace("$", "").replace(",", "") if original_price_tag else "N/A"
        # Extract savings
        savings_tag = bike_tile.find('div', class_='productTile__priceSave')
        savings = savings_tag.text.strip().replace("You save $", "").replace(",", "") if savings_tag else "N/A"
        # Extract discount percentage
        badge_tile = bike_tile.find('div', class_='productTileDefault__awardAndBadges')
        if badge_tile:
            discount_tag = badge_tile.find('div', class_='productBadge productBadge--pricing')
            discount_percentage = discount_tag.text.strip().replace("-", "").replace("%", "") if discount_tag else "N/A"
        else:
            discount_percentage = "N/A"
        # Extract highlights
        highlights_tag = bike_tile.find('div', class_='productTileDefault__info--highlights')
        highlights = highlights_tag.text.strip() if highlights_tag else "N/A"
        # Extract promotional information
        promo_tag = bike_tile.find('div', class_='productTileDefault__info--promo')
        promotion = promo_tag.text.strip() if promo_tag else "N/A"
        # Extract color
        color_tag = bike_tile.find('span', class_='colorSwatch__colorLabelValue')
        color = color_tag.text.strip() if color_tag else "N/A"
        # Extract image URL
        # Extract image URL directly from the correct <img> tag
        image_tag = bike_tile.find('img', class_='picture__image productTileDefault__image')
        image_url = image_tag['src'] if image_tag else "N/A"

        # link to full bike details page
        link_tag = bike_tile.find('a', class_='productTileDefault__productName')
        bike_link = link_tag['href'] if link_tag else "N/A"

        # Append extracted data
        results.append({
            "Name": name,
            "Sale Price": sale_price,
            "Original Price": original_price,
            "Savings": savings,
            "Discount Percentage": discount_percentage,
            "Highlights": highlights,
            "Promotion": promotion,
            "Color": color,
            "Image URL": image_url,
            "Bike Link": bike_link
        })
    # Convert results to a pandas DataFrame
    df = pd.DataFrame(results)
    return df
def generate_html_report(df, output_file="canyon_bikes_report.html"):
    # Start building the HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Canyon Bikes Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 20px;
                background-color: #f8f9fa;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                padding: 10px;
                text-align: left;
                border: 1px solid #ddd;
            }
            th {
                background-color: #6c757d;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            img {
                max-width: 150px;
                height: auto;
            }
        </style>
    </head>
    <body>
        <h1>Canyon Bikes Report</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Sale Price</th>
                    <th>Original Price</th>
                    <th>Savings</th>
                    <th>Discount (%)</th>
                    <th>Highlights</th>
                    <th>Promotion</th>
                    <th>Color</th>
                    <th>Image</th>
                </tr>
            </thead>
            <tbody>
    """
    # Add rows to HTML table from the DataFrame
    for _, row in df.iterrows():
        html_content += f"""
                <tr>
                    <td>{row['Name']}</td>
                    <td>${row['Sale Price']}</td>
                    <td>${row['Original Price']}</td>
                    <td>${row['Savings']}</td>
                    <td>{row['Discount Percentage']}%</td>
                    <td>{row['Highlights']}</td>
                    <td>{row['Promotion']}</td>
                    <td>{row['Color']}</td>
                    <td><img src="{row['Image URL']}" alt="{row['Name']}"></td>
                </tr>
        """
    # Close HTML table and document
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"HTML report generated: {output_file}")

# Example Usage
if __name__ == '__main__':
    # # Load your HTML content either from a file or by fetching from a website
    # with open('example.html', 'r', encoding='utf-8') as file:  # Replace with your file containing HTML
    #     html_content = file.read()
    gravel_outlet_url = "https://www.canyon.com/en-us/outlet-bikes/gravel-bikes/?prefn1=pc_rahmengroesse&prefv1=XS&srule=bestsellers_sale_CUS"
    road_outlet_url = "https://www.canyon.com/en-us/outlet-bikes/road-bikes/?prefn1=pc_rahmengroesse&prefv1=XS&srule=bestsellers_sale_CUS"
    # road_url = "https://www.canyon.com/en-us/road-bikes/endurance-bikes/?prefn1=pc_rahmengroesse&prefv1=XS&srule=sort_master_availabilityUS"
    
    
    # Scrape Canyon gravel bikes from the outlet page
    gravel_bikes_data = scrape_canyon_bikes(gravel_outlet_url)
    road_bikes_data = scrape_canyon_bikes(road_outlet_url)

    # Combine the dataframes
    bikes_data = pd.concat([road_bikes_data, gravel_bikes_data], ignore_index=True)

    # Scrape the bikes data
    # bikes_data = scrape_canyon_bikes(html_content)
    print(bikes_data)
    # Save as CSV
    bikes_data.to_csv('canyon_bikes.csv', index=False)
    # Print the first few rows
    print(bikes_data.head())

    # Generate HTML report
    generate_html_report(bikes_data, output_file="canyon_bikes_report.html")