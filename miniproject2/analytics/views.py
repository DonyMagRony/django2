import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .models import APIRequestLog, CourseMetric
from django.db.models import Count

def api_usage_graph(request):
    data = (
        APIRequestLog.objects.using('analytics')
        .values('endpoint')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    endpoints = [item['endpoint'] for item in data]
    counts = [item['count'] for item in data]

    plt.figure(figsize=(10, 6))
    plt.bar(endpoints, counts, color='skyblue')
    plt.xlabel('Endpoints')
    plt.ylabel('Requests')
    plt.title('API Usage per Endpoint')
    plt.xticks(rotation=45, ha='right')

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph_base64 = base64.b64encode(image_png).decode('utf-8')
    buffer.close()

    return render(request, 'templates/templates_analytics/graph.html', {'graph': graph_base64})


def most_active_users(request):
    data = (
        APIRequestLog.objects.using('analytics')
        .values('user__username')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    users = [item['user__username'] for item in data]
    counts = [item['count'] for item in data]

    plt.figure(figsize=(10, 6))
    plt.bar(users, counts, color='green')
    plt.xlabel('Users')
    plt.ylabel('Requests')
    plt.title('Most Active Users')
    plt.xticks(rotation=45, ha='right')

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph_base64 = base64.b64encode(image_png).decode('utf-8')
    buffer.close()

    return render(request, 'templates/templates_analytics/graph.html', {'graph': graph_base64})
