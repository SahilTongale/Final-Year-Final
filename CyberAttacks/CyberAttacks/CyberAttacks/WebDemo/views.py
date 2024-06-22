from django.shortcuts import render

# Create your views here.
def index(request):
    # Access data set by middleware
    request_count = request.META.get('request_count', 0)
    client_ip = request.META.get('client_ip', 'Unknown')
    source = request.META.get('source',"Unknown")
    print(request_count,client_ip,source)
    all = request.META.get("all",None)
    print(all)

    return render(request,"index.html",context={'request_count': request_count, 'client_ip': client_ip,'source':source,'all':all})