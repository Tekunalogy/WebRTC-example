var peer_connection = null;

// Declare a function that will be used to establish a peer-to-peer connection and initiate a video stream.
function negotiate() {
    /**
     * Transceiver is a channel used for streaming media:
     *  - specific type (audio, video)
     *  - specific direction (send, receive)
     * We are creating a transceiver for receiving video.
     */
    peer_connection.addTransceiver('video', {direction: 'recvonly'});

    // Create an offer to start the call
    return peer_connection.createOffer().then(function(offer) {
        // Set the local description of the peer connection to the offer.
        return peer_connection.setLocalDescription(offer);

    }).then(function() {
        /**
         * ICE (Interactive Connectivity Establishment)
         * Wait for the ICE gathering process to complete before continuing:
         * Gathers:
         * - local network addresses
         * - candidate transport addresses
         * Exchanges this info with the remote peer to establish a connection.
         */
        return new Promise(function(resolve) {
            // If the ICE gathering process is already complete, resolve the promise immediately.
            if (peer_connection.iceGatheringState === 'complete') {
                resolve();
            }
            // If not, wait for the gathering state to change to 'complete' before resolving the promise.
            else {
                function checkState() {
                    if (peer_connection.iceGatheringState === 'complete') {
                        peer_connection.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                peer_connection.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        // Fetch the local description of the peer connection (the python client sending video)
        var offer = peer_connection.localDescription;
        return fetch('http://127.0.0.1:8080/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
                device_id: "/dev/video2"
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        // Receive the answer from the server
        return response.json();
    }).then(function(answer) {
        // set the remote description of the peer connection
        console.log(answer)
        return peer_connection.setRemoteDescription(answer);
    }).catch(function(e) {
        // If there is an error at any point, display an alert with the error message.
        alert(e);
    });
}

// Declare a function that will be used to start the video call.
function start() {
    /**
     * Set the SDP semantics configuration for the peer connection
     * SDP: Session Description Protocol
     * 
     * The "unified plan" format allows for greater flexibility in negotiating media streams,
     * and allows for easier handling of media streams with multiple tracks.
     * Useful in scenarios where multiple cameras or microphones are available on a device
     */
    var config = {
        sdpSemantics: 'unified-plan'
    };

    // Create a new peer connection with the specified configuration.
    peer_connection = new RTCPeerConnection(config);

    // When a new track is added to the peer connection, set the source of the 'video' element to the stream.
    peer_connection.addEventListener('track', function(evt) {
        document.getElementById('video').srcObject = evt.streams[0];
    });

    // Hide the 'Start' button and initiate the call.
    document.getElementById('start').style.display = 'none';
    negotiate();

    // Show the 'Stop' button.
    document.getElementById('stop').style.display = 'inline-block';
}

// Declare a function that will be used to stop the video call.
function stop() {
    // Hide the 'Stop' button.
    document.getElementById('stop').style.display = 'none';

    // Close the peer connection after a short delay.
    setTimeout(function() {
        peer_connection.close();
    }, 500);
}
