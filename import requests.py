import requests
from bs4 import BeautifulSoup
import pandas as pd  
from datetime import datetime
    
def get_data(url, pages, size):
    reviews = pd.DataFrame(columns=["Date", "Rating", "Headline", "Verified", 
        "Aircraft", "Traveller", "Seat Type", "Route", "Date Flown",
        "Seat Comfort", "Cabin Staff Service", "Food & Beverages",
        "Inflight Entertainment", "Ground Service", "Wifi & Connectivity",
        "Value For Money", "Recommended", "Review"])
     
    for i in range(1,pages + 1):
        r = requests.get(url + f"/page/{i}/?sortby=post_date:Desc&pagesize={size}")
        
        print(f"Page Number : {i}") 
        soup = BeautifulSoup(r.content, 'html.parser')
        
        per_review_container = soup.find_all("article", itemprop="review")
        
        for review in per_review_container:
            # Rating
            rating = review.find("span", itemprop="ratingValue")
            rating = int(rating.text.strip() if rating else None)
            
            # Date Published
            date = review.find("time", itemprop="datePublished")
            date = date.text.strip() if date else None            
            
            #Headline
            headline = review.find("h2", class_="text_header")
            headline = headline.text.strip() if rating else None
            
            # Review Body
            review_text = review.find("div", itemprop="reviewBody")
            review_text = str(review_text.text.strip() if rating else None )
            review_text = review_text.split("|")
            review_body = review_text[1].strip() if len(review_text) > 1 else None
            
            # Verification Status
            verified = review_text[0].strip() if len(review_text) > 1 else None
            verified = True if verified == "✅ Trip Verified" else False
            
            # Additonnal Statistics 
            review_stats = {}
            stats = review.find_all("tr")
            for stat in stats:
                header = stat.find("td", class_="review-rating-header")
                value = stat.find("td", class_="review-value") or stat.find("td", class_="review-rating-stars")
                if header and value:
                    key = header.text.strip()
                    if value.get("class") and "stars" in value.get("class"):
                        stars = value.find_all("span", class_="star")
                        rating_value = sum(1 for star in stars if "fill" in star.get("class", []))
                        review_stats[key] = f"{rating_value} stars"
                    else:
                        review_stats[key] = value.text.strip()

            reviews.loc[len(reviews)] = [date,
                                            rating,
                                            headline,
                                            verified,
                                            review_stats.get("Aircraft"),
                                            review_stats.get("Type Of Traveller"),
                                            review_stats.get("Seat Type"),
                                            review_stats.get("Route"),
                                            review_stats.get("Date Flown"),
                                            review_stats.get("Seat Comfort"),
                                            review_stats.get("Cabin Staff Service"),
                                            review_stats.get("Food & Beverages"),
                                            review_stats.get("Inflight Entertainment"),
                                            review_stats.get("Ground Service"),
                                            review_stats.get("Wifi & Connectivity"),
                                            review_stats.get("Value For Money"),
                                            review_stats.get("Recommended"),
                                            review_body]
            
    return reviews

def data_cleaning(df):
    df["Date"] = pd.to_datetime(df["Date"], format="mixed")
    
    df["Headline"] = df["Headline"].str.strip('"')
    
    df["Aircraft"] = df["Aircraft"].fillna("Unknown")
    
    df["Traveller"] = df["Traveller"].fillna("Unknown")
    
    df["Route"] = df["Route"].fillna("Unknown")
    df["Route"] = df["Route"].str.strip()
    
    df[["From", "To"]] = df["Route"].str.split(" to ", n=1, expand=True)
    df["Via"] = df["To"].str.split(" via ", n=1).str[1]
    df["To"] = df["To"].str.split(" via ", n=1).str[0]
    
    df["Stops"] = df["Via"].notna().map({True: "1 stop", False: "Direct"})
    
    return df

def data_exploration(df, column):
    if column not in df.columns:
        print(f"Error: Column '{column}' not found in the DataFrame.")
        return
    
    print(f"Exploring Column: '{column}'\n")
    
    print("1. Data Type:")
    print(f"   {df[column].dtype}\n")
    
    unique_values = df[column].unique()
    print("2. Unique Values:")
    print(f"   Count: {len(unique_values)}")
    print(f"   Values: {unique_values[:10]}{'...' if len(unique_values) > 10 else ''}\n")
    
    print("3. Value Counts:")
    print(df[column].value_counts())
    
    missing_count = df[column].isnull().sum()
    print("\n4. Missing Values:")
    print(f"   Count: {missing_count}")
    print(f"   Percentage: {missing_count / len(df) * 100:.2f}%\n")
    
    if pd.api.types.is_numeric_dtype(df[column]):
        print("5. Statistical Summary:")
        print(df[column].describe())
        print("\n")

    
def main():
    url = "https://www.airlinequality.com/airline-reviews/british-airways"
    pages = 10
    size = 100
    
    df = get_data(url, pages, size)
    
    df = data_cleaning(df)
    
    data_exploration(df, "Seat Comfort")
    
    print(df.info())
    print(df)
    
    # df.to_csv("british_airways_reviews.csv", index=False)

if __name__ == "__main__":
    main()