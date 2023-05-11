package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/pion/mediadevices"
	"github.com/pion/mediadevices/pkg/codec/x264"
	"github.com/pion/mediadevices/pkg/prop"
	"github.com/pion/webrtc/v3"

	_ "github.com/pion/mediadevices/pkg/driver/camera" // This is required to register camera adapter
)

type body struct {
	TYPE      string `json:"type"`
	SDP       string `json:"sdp"`
	DEVICE_ID string `json:"device_id"`
}

func main() {
	r := mux.NewRouter()

	// Add the CORS middleware handler
	r.Use(corsMiddleware)

	// Create a new HTTP handler that serves the WebRTC offer
	r.HandleFunc("/offer", func(w http.ResponseWriter, r *http.Request) {

		var http_body body
		err := json.NewDecoder(r.Body).Decode(&http_body)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		offer := webrtc.SessionDescription{
			Type: webrtc.NewSDPType(http_body.TYPE),
			SDP:  http_body.SDP,
		}

		// Create video params for peer connection
		x264Params, err := x264.NewParams()
		if err != nil {
			panic(err)
		}
		x264Params.BitRate = 4_000_000 // 4mbps

		codecSelector := mediadevices.NewCodecSelector(
			mediadevices.WithVideoEncoders(&x264Params),
		)

		config := webrtc.Configuration{}
		mediaEngine := webrtc.MediaEngine{}
		codecSelector.Populate(&mediaEngine)
		api := webrtc.NewAPI(webrtc.WithMediaEngine(&mediaEngine))

		// Create a new RTCPeerConnection
		peerConnection, err := api.NewPeerConnection(config)
		if err != nil {
			panic(err)
		}

		peerConnection.OnICEConnectionStateChange(func(connectionState webrtc.ICEConnectionState) {
			fmt.Printf("Connection State has changed: %s \n", connectionState.String())
		})

		s, err := mediadevices.GetUserMedia(mediadevices.MediaStreamConstraints{
			Video: func(c *mediadevices.MediaTrackConstraints) {
				c.DeviceID = prop.String("/dev/video0")
				c.Width = prop.Int(1280)
				c.Height = prop.Int(720)
			},
			Codec: codecSelector,
		})
		if err != nil {
			panic(err)
		}

		for _, track := range s.GetTracks() {
			track.OnEnded(func(err error) {
				fmt.Printf("Track (ID: %s) ended with error: %v\n",
					track.ID(), err)
			})

			_, err = peerConnection.AddTransceiverFromTrack(track,
				webrtc.RtpTransceiverInit{
					Direction: webrtc.RTPTransceiverDirectionSendonly,
				},
			)
			if err != nil {
				panic(err)
			}
		}

		// Set the remote SessionDescription
		err = peerConnection.SetRemoteDescription(offer)
		if err != nil {
			panic(err)
		}

		// Create an answer
		answer, err := peerConnection.CreateAnswer(nil)
		if err != nil {
			panic(err)
		}

		// Create channel that is blocked until ICE Gathering is complete
		gatherComplete := webrtc.GatheringCompletePromise(peerConnection)

		// Sets the LocalDescription, and starts our UDP listeners
		err = peerConnection.SetLocalDescription(answer)
		if err != nil {
			panic(err)
		}

		json, err := json.Marshal(peerConnection.LocalDescription())
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(json)

		fmt.Println("huhhhh???")

		// Block until ICE Gathering is complete, disabling trickle ICE
		// we do this because we only can exchange one signaling message
		// in a production application you should exchange ICE Candidates via OnICECandidate
		<-gatherComplete

	})

	// Start serving HTTP requests
	log.Println("Listening at http://localhost:8080/offer")
	log.Fatal(http.ListenAndServe(":8080", r))
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Set the Access-Control-Allow-Origin header to allow all origins
		w.Header().Set("Access-Control-Allow-Origin", "*")

		// Handle CORS preflight request
		if r.Method == http.MethodOptions {
			// Set the Access-Control-Allow-Methods header to allow GET, POST, PUT, and DELETE
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
			// Set the Access-Control-Allow-Headers header to allow all headers
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
			w.Header().Set("Access-Control-Max-Age", "86400")
			w.WriteHeader(http.StatusOK)
			return
		}

		// Call the next middleware handler in the chain
		next.ServeHTTP(w, r)
	})
}
