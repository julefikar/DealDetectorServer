from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()

'''
    curl "https://api.priceapi.com/v2/jobs" 
>         -X POST \
>         -d "token=OCNXKSNMBFLRRLWZWANKMIOLWSVWEAUYBCHWCADJLMYTVBAVKKNJGPFNZLUDXTVG" \
>         -d "country=us" \
>         -d "source=google_shopping" \
>         -d "topic=product_and_offers" \
>         -d "key=term" \
>         -d "max_age=1200" \
>         -d "max_pages=1" \
>         -d "sort_by=ranking_descending" \
>         -d "condition=any" \
>         -d "shipping=any" \
>         -d 'values=light blue jeans' 

'''