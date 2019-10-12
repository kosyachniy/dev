import React from 'react';
import openSocket from 'socket.io-client';

import { socket } from '../sets';


export default class App extends React.Component {
	constructor(props) {
		super(props);

		const stun = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
		this.peer = new RTCPeerConnection(stun);

		this.type = document.location.search.split('=')[1];

		this.yourDescription = null;
		this.otherDescription = null;
		this.yourCandidate = null;
		this.newCandidate = null;

		this.answer = this.answer.bind(this);
		this.call = this.call.bind(this);
		this.connect = this.connect.bind(this);

		this.candidate1 = null;
		this.description1 = null;
		this.candidate2 = null;
		this.description2 = null;

		this.sio = null;

		this.sended = 0;
	}

	componentDidMount() {
		const namespace = 'space';
		this.sio = openSocket(socket.link + namespace);
		if (this.type === 'student') {
			this.peer.onicecandidate = e => {
				if (e.candidate) {
					this.yourCandidate = e.candidate;
					if (this.yourCandidate) {
						this.sended++;
						console.log(this.sended, this.yourCandidate)
						console.log('!', this.sended)
						this.sio.emit('candidate2', this.yourCandidate);
					}
				}
			}

			this.sio.on('candidate1', (mes) => {
				console.log('!cand1', mes)
				this.peer.addIceCandidate(mes);
			});

			this.sio.on('description1', (mes) => {
				console.log('!desc1', mes)
				this.description1 = mes;
				this.answer();
			});
		} else {
			this.peer.onicecandidate = e => {
				if (e.candidate) {
					this.yourCandidate = e.candidate;
					if (this.yourCandidate) {
						this.sended++;
						console.log(this.sended, this.yourCandidate)

						console.log('!', this.sended)
						this.sio.emit('candidate1', this.yourCandidate);
					}
				}
			}

			this.call();
			this.call();

			this.sio.on('candidate2', (mes) => {
				console.log('!cand2', mes)
				this.peer.addIceCandidate(mes);
			});

			this.sio.on('description2', (mes) => {
				console.log('!desc2', mes)
				this.description2 = mes;
				this.connect();
			});
		}
	}

	call() {
		navigator.mediaDevices.getUserMedia({ video: true, audio: true })
		.then(stream => {
			const videoLocal = document.getElementById('local');
			videoLocal.autoplay = true;
			videoLocal.muted = true;
			videoLocal.srcObject = stream;
			// iOS
			let peer = this.peer;
			stream.getTracks().forEach(function(track) {
				peer.addTrack(track, stream);
			});

			return this.peer.createOffer();
		})
		.then(offer => {
			// Mozilla
			this.peer.setLocalDescription(new RTCSessionDescription(offer)).then(
				() => {
					this.yourDescription = this.peer.localDescription;
					if (this.yourDescription) {
						this.sio.emit('description1', this.yourDescription);
					}
				}
			)

		})

		this.peer.ontrack = e => {
			document.getElementById("remote").srcObject = e.streams[0];
		}
	}

	connect() {
		this.peer.setRemoteDescription(this.description2)
	}

	answer() {
		navigator.mediaDevices.getUserMedia({ video: true, audio: true })
		.then(stream => {
			const videoLocal = document.getElementById('local');
			videoLocal.autoplay = true;
			videoLocal.muted = true;
			videoLocal.srcObject = stream;
			// iOS
			let peer = this.peer;
			stream.getTracks().forEach(function(track) {
				peer.addTrack(track, stream);
			});

			this.peer.setRemoteDescription(this.description1);
		})
		.then(() => this.peer.createAnswer())
		.then(answer => {
			// Mozilla
			this.peer.setLocalDescription(new RTCSessionDescription(answer)).then(() => {
				this.yourDescription = this.peer.localDescription;
				if (this.yourDescription) {
					this.sio.emit('description2', this.yourDescription);
				}
			})
		})

		this.peer.ontrack = e => {
			document.getElementById("remote").srcObject = e.streams[0];
		}
	}

	render() {
		return (
			<>
				<div>
					<video id="local" autoPlay controls></video>
					<video id="remote" autoPlay controls></video>
				</div>
			</>
		)
	}
}
