/* Adapted from https://github.com/muaz-khan/RecordRTC/blob/master/index.html */
var recordingDIV = document.querySelector('.recordrtc');
var recordingPlayer = recordingDIV.querySelector('video.rtcvideo');
var mimeType = 'video/webm\;codecs=vp8';
var fileExtension = 'webm';
var type = 'video';
var defaultWidth;
var defaultHeight;
var timeSlice = false;

var btnStartRecording = document.querySelector('#btn-start-recording');

recordingPlayer.style.display = 'none';

window.onbeforeunload = function() {
    btnStartRecording.disabled = false;
};

btnStartRecording.onclick = function(event) {
    var button = btnStartRecording;

    if(button.innerHTML === stop_text) {
        button.disabled = true;
        button.disableStateWaiting = true;
        setTimeout(function() {
            button.disabled = false;
            button.disableStateWaiting = false;
        }, 2 * 1000);

        button.innerHTML = start_recording_text;

        function stopStream() {
            if(button.stream && button.stream.stop) {
                var tracks = button.stream.getTracks();
                // Stop each track instead of stopping the whole stream.
                tracks.forEach(function(track) {
                    track.stop();
                });
                button.stream = null;
            }
            videoBitsPerSecond = null;
        }

        if(button.recordRTC) {
            button.recordRTC.stopRecording(function(url) {
                if(button.blobs && button.blobs.length) {
                    var blob = new File(button.blobs, getFileName(fileExtension), {
                        type: mimeType
                    });

                    button.recordRTC.getBlob = function() {
                        return blob;
                    };

                    url = URL.createObjectURL(blob);
                }

                button.recordingEndedCallback(url);
                saveToDiskOrOpenNewTab(button.recordRTC);
                stopStream();
            });
        }

        return;
    }

    if(!event) return;

    button.disabled = true;

    var commonConfig = {
        onMediaCaptured: function(stream) {
            button.stream = stream;
            if(button.mediaCapturedCallback) {
                button.mediaCapturedCallback();
            }

            button.innerHTML = stop_recording_text;
            button.disabled = false;
        },
        onMediaStopped: function() {
            button.innerHTML = start_recording_text;

            if(!button.disableStateWaiting) {
                button.disabled = false;
            }
        },
        onMediaCapturingFailed: function(error) {
            console.error('onMediaCapturingFailed:', error);
            commonConfig.onMediaStopped();
        }
    };

    // Record camera
    captureVideo(commonConfig);

    var options = {
        type: type,
        mimeType: mimeType,
        disableLogs: params.disableLogs || false,
        //getNativeBlob: false, // enable it for longer recordings
        video: recordingPlayer
    };

    button.mediaCapturedCallback = function() {
        if(videoBitsPerSecond) {
            options.videoBitsPerSecond = videoBitsPerSecond;
        }

        button.recordRTC = RecordRTC(button.stream, options);

        button.recordingEndedCallback = function(url) {
            setVideoURL(url);
        };

        button.recordRTC.startRecording();
    };
};

function captureVideo(config) {
    var constraints = {
        audio: false,
        video: {
            width: { ideal: 1280, max: 1920 },
            height: { ideal: 720, max: 1080 }
        }
    }
    captureUserMedia(constraints, function(videoStream) {
        config.onMediaCaptured(videoStream);

        addStreamStopListener(videoStream, function() {
            config.onMediaStopped();
        });
    }, function(error) {
        config.onMediaCapturingFailed(error);
    });
}

var videoBitsPerSecond;

function captureUserMedia(mediaConstraints, successCallback, errorCallback) {
    if(mediaConstraints.video == true) {
        mediaConstraints.video = {};
    }
    videoBitsPerSecond = null;
    // getUserMedia
    navigator.mediaDevices.getUserMedia(mediaConstraints).then(function(stream) {
        successCallback(stream);

        setVideoURL(stream);
    }).catch(function(error) {
        if(error && error.name === 'ConstraintNotSatisfiedError') {
            alert(resolution_error_text);
        }

        errorCallback(error);
    });
}

function saveToDiskOrOpenNewTab(recordRTC) {
    var fileName = getFileName(fileExtension);

    // upload to server
    recordingDIV.querySelector('#upload-to-server').parentNode.style.display = 'block';
    recordingDIV.querySelector('#upload-to-server').disabled = false;
    recordingDIV.querySelector('#upload-to-server').onclick = function() {
        if(!recordRTC) return alert(no_recording_found_text);
        this.disabled = true;

        var button = this;
        uploadToServer(fileName, recordRTC, function(progress, fileURL) {
            if(progress === 'ended') {
                button.disabled = false;
                button.innerHTML = download_text;
                var alert = document.createElement("div");
                alert.setAttribute('class', 'alert alert-success');
                alert.innerHTML = upload_completed_text;
                button.parentNode.appendChild(alert);
                button.onclick = function() {
                    SaveFileURLToDisk(fileURL, fileName);
                };

                setVideoURL(fileURL);
                return;
            }
            button.innerHTML = progress;
        });
    };
}

function uploadToServer(fileName, recordRTC, callback) {
    var blob = recordRTC instanceof Blob ? recordRTC : recordRTC.getBlob();

    blob = new File([blob], getFileName(fileExtension), {
        type: mimeType
    });

    // create FormData
    var formData = new FormData();
    formData.append('videofile', blob);
    formData.append('gloss', gloss_pk);
    formData.append('csrfmiddlewaretoken', csrf_token);

    callback('Uploading recorded-file to server.');

    makeXMLHttpRequest('/video/upload/recorded/', formData, function(progress, responseJSON) {
        if (progress !== 'upload-ended') {
            callback(progress);
            return;
        }
        responseJSON = JSON.parse(responseJSON);
        // Parse the video id from json key 'videoid'
        var initialURL = '/video/'+responseJSON["videoid"]+'/';
        callback('ended', initialURL);
    });
}

function makeXMLHttpRequest(url, data, callback) {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            // Get video id, so that we can link to the created one
            callback('upload-ended', request.response);
        }
    };

    request.upload.onloadstart = function() {
        callback('Upload started');
    };

    request.upload.onprogress = function(event) {
        callback('Upload Progress ' + Math.round(event.loaded / event.total * 100) + "%");
    };

    request.upload.onload = function() {
        callback('progress-about-to-end');
    };

    request.upload.onload = function() {
        callback('progress-ended');
    };

    request.upload.onerror = function(error) {
        callback('Failed to upload to server');
    };

    request.upload.onabort = function(error) {
        callback('Upload aborted.');
    };

    request.upload.onloadend = function() {
        callback('Done.');
    }

    request.open('POST', url);
    request.send(data);
}

function getRandomString() {
    if (window.crypto && window.crypto.getRandomValues && navigator.userAgent.indexOf('Safari') === -1) {
        var a = window.crypto.getRandomValues(new Uint32Array(3)),
            token = '';
        for (var i = 0, l = a.length; i < l; i++) {
            token += a[i].toString(36);
        }
        return token;
    } else {
        return (Math.random() * new Date().getTime()).toString(36).replace(/\./g, '');
    }
}
function getFileName(fileExtension) {
    return 'RecordRTC-' + (new Date).toISOString().replace(/:|\./g, '-')+ '-' + getRandomString() + '.' + fileExtension;
}

function SaveFileURLToDisk(fileUrl, fileName) {
    var hyperlink = document.createElement('a');
    hyperlink.href = fileUrl;
    hyperlink.target = '_blank';
    hyperlink.download = fileName || fileUrl;

    (document.body || document.documentElement).appendChild(hyperlink);
    hyperlink.onclick = function() {
       (document.body || document.documentElement).removeChild(hyperlink);

        // required for Firefox
        window.URL.revokeObjectURL(hyperlink.href);
    };

    var mouseEvent = new MouseEvent('click', {
        view: window,
        bubbles: true,
        cancelable: true
    });

    hyperlink.dispatchEvent(mouseEvent);

}

function getURL(arg) {
    var url = arg;

    if(arg instanceof Blob || arg instanceof File) {
        url = URL.createObjectURL(arg);
    }

    if(arg instanceof RecordRTC || arg.getBlob) {
        url = URL.createObjectURL(arg.getBlob());
    }

    return url;
}

function setVideoURL(arg) {
    var url = getURL(arg);

    var parentNode = recordingPlayer.parentNode;
    parentNode.removeChild(recordingPlayer);
    parentNode.innerHTML = '';

    var elem = 'video';

    recordingPlayer = document.createElement(elem);

    if(arg instanceof MediaStream) {
        recordingPlayer.muted = true;
    }

    recordingPlayer.addEventListener('loadedmetadata', function() {
        if(navigator.userAgent.toLowerCase().indexOf('android') == -1) return;

        // android
        setTimeout(function() {
            if(typeof recordingPlayer.play === 'function') {
                recordingPlayer.play();
            }
        }, 2000);
    }, false);

    recordingPlayer.poster = '';

    if(arg instanceof MediaStream) {
        recordingPlayer.srcObject = arg;
    }
    else {
        recordingPlayer.src = url;
    }

    if(typeof recordingPlayer.play === 'function') {
        recordingPlayer.play();
    }

    recordingPlayer.controls = true;
    parentNode.appendChild(recordingPlayer);
}
