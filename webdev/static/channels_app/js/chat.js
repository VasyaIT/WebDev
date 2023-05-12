    const roomName = JSON.parse(document.getElementById('json-roomname').textContent);
    const userName = JSON.parse(document.getElementById('json-username').textContent);
    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
        + roomName
        + '/'
    );

    chatSocket.onclose = function(e) {
        console.log('onclose')
    }

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

//        var objToday = new Date(),
//            dayOfMonth = today + ( objToday.getDate() < 10) ? '0' + objToday.getDate() : objToday.getDate(),
//            months = new Array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
//            curMonth = months[objToday.getMonth()],
//            curHour = objToday.toUTCString(),
//            curMinute = objToday.toUTCString() < 10 ? "0" + objToday.getMinutes() : objToday.getMinutes();
//
//        var today = dayOfMonth + " " + curMonth + ' ' + curHour + ":" + curMinute;


        if (data.message) {
            document.querySelector('#chat-messages').innerHTML += ('<b>' + data.username + '</b>: ' + data.message + '<br>' + '<small>now</small><br>');
        }

        scrollToBottom();
    };

    document.querySelector('#chat-message-input').focus();
    document.querySelector('#chat-message-input').onkeyup = function(e) {
        if (e.keyCode === 13) {
            document.querySelector('#chat-message-submit').click();
        }
    };

    document.querySelector('#chat-message-submit').onclick = function(e) {
        e.preventDefault()

        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;

        console.log({
            'message': message,
            'username': userName,
            'room': roomName
        })

        chatSocket.send(JSON.stringify({
            'message': message,
            'username': userName,
            'room': roomName
        }));

        messageInputDom.value = '';

        return false
    };

    /**
    * A function for finding the messages element, and scroll to the bottom of it.
    */
    function scrollToBottom() {
        let objDiv = document.getElementById("chat-messages");
        objDiv.scrollTop = objDiv.scrollHeight;
    }

    // Add this below the function to trigger the scroll on load.
    scrollToBottom();