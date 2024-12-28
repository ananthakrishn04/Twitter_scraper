from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.core.serializers import serialize
from .scrape import TwitterTrendsScraper
from .models import Trend
import datetime
import uuid
import json

def index(request):
    if request.method == "POST":

        try:
            scraper = TwitterTrendsScraper(settings.TWITTER_USERNAME,settings.TWITTER_PASSWORD,settings.TWITTER_EMAIL)
            trending_topics , ip = scraper.run_scraper()
            timestamp = datetime.datetime.now()

            unique_id = str(uuid.uuid4())

            record = Trend(
                _id=unique_id,
                trend1=trending_topics[0] if len(trending_topics) > 0 else None,
                trend2=trending_topics[1] if len(trending_topics) > 1 else None,
                trend3=trending_topics[2] if len(trending_topics) > 2 else None,
                trend4=trending_topics[3] if len(trending_topics) > 3 else None,
                trend5=trending_topics[4] if len(trending_topics) > 4 else None,
                datetime=timestamp,
                ip_address=ip,
            )

            record.save()

            queryset = Trend.objects.all()[:5]  # Replace `Trend` with your model
            serialized_data = json.loads(serialize('json', queryset)) 

            return render(request, "index.html", {"result": trending_topics[:5] , "datetime" : timestamp,"ip_address":ip , 'data' : serialized_data })
        
        except Exception as e:
            return HttpResponse(e)
    
    return render(request, "index.html")

