from django.shortcuts import render


def main(request):
    return render(request, 'chat/main.html')


def chat_detail(request, room_name):
    context = {
        'room_name': room_name
    }
    return render(request, 'chat/chat_detail.html', context)
