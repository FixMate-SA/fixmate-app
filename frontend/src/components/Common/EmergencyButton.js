import React, { useState, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { getApiUrl } from '../../utils/api';

const EmergencyButton = ({ jobId = null, className = '', size = 'normal' }) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [isEmergency, setIsEmergency] = useState(false);
  const [loading, setLoading] = useState(false);
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState(null);
  const [alertSent, setAlertSent] = useState(false);
  const [step, setStep] = useState('initial'); // initial, recording, processing, sent
  
  // Voice recording states
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [playingAudio, setPlayingAudio] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingIntervalRef = useRef(null);
  const audioPlayerRef = useRef(null);

  const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 30000
        }
      );
    });
  };

  const getLocationAddress = async (lat, lng) => {
    try {
      const response = await fetch(
        getApiUrl(`/emergency/location?latitude=${lat}&longitude=${lng}`)
      );
      const data = await response.json();
      return data.address || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    } catch (error) {
      return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }
  };

  const handleEmergencyClick = () => {
    setIsEmergency(true);
    setStep('initial');
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg'
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      setRecordingTime(0);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorder.mimeType 
        });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(100); // Record in 100ms chunks
      setIsRecording(true);
      setStep('recording');

      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => {
          if (prev >= 120) { // Maximum 2 minutes
            stopRecording();
            return 120;
          }
          return prev + 1;
        });
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      alert(t('microphoneAccessError', 'Unable to access microphone. Please check permissions and try again.'));
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(recordingIntervalRef.current);
    }
  };

  const playRecording = () => {
    if (audioBlob && !playingAudio) {
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audioPlayerRef.current = audio;
      
      audio.onended = () => {
        setPlayingAudio(false);
        URL.revokeObjectURL(audioUrl);
      };
      
      audio.play();
      setPlayingAudio(true);
    } else if (audioPlayerRef.current && playingAudio) {
      audioPlayerRef.current.pause();
      setPlayingAudio(false);
    }
  };

  const deleteRecording = () => {
    if (audioBlob) {
      setAudioBlob(null);
      setRecordingTime(0);
      setStep('initial');
    }
  };

  const sendEmergencyAlert = async () => {
    if (!user) return;

    setLoading(true);
    setStep('processing');

    try {
      // Get current location
      const position = await getCurrentLocation();
      const address = await getLocationAddress(position.latitude, position.longitude);
      
      setLocation({ ...position, address });

      // Create FormData for emergency alert with voice recording
      const formData = new FormData();
      formData.append('user_id', user.id);
      formData.append('user_name', user.name || user.first_name + ' ' + user.last_name || 'Unknown');
      formData.append('user_phone', user.phone || 'Unknown');
      formData.append('job_id', jobId || '');
      formData.append('alert_type', 'emergency');
      formData.append('latitude', position.latitude.toString());
      formData.append('longitude', position.longitude.toString());
      formData.append('address', address);
      formData.append('description', description || 'Emergency assistance requested');
      formData.append('priority', 'high');
      
      // Add voice recording if available
      if (audioBlob) {
        formData.append('voice_recording', audioBlob, `emergency_${user.id}_${Date.now()}.webm`);
        formData.append('recording_duration', recordingTime.toString());
      }

      const response = await fetch(getApiUrl('/emergency/alert'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token') || localStorage.getItem('fixmate_client_token') || localStorage.getItem('fixmate_fixer_token')}`
        },
        body: formData
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setAlertSent(true);
        setStep('sent');
        
        // Show success notification
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('Emergency Alert Sent', {
            body: 'Your emergency alert has been sent to FixMate emergency services. Help is being dispatched.',
            icon: '/fixmate-logo.jpg'
          });
        }
      } else {
        throw new Error(result.detail || 'Failed to send emergency alert');
      }
    } catch (error) {
      console.error('Emergency alert failed:', error);
      alert(t('emergencyAlertFailed', 'Failed to send emergency alert. Please call 10111 directly for immediate assistance.\n\nError: ') + error.message);
      
      // Provide direct fallback
      if (confirm(t('callPoliceDirectly', 'Would you like to call 10111 directly now?'))) {
        window.open('tel:10111', '_self');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    // Stop recording if active
    if (isRecording) {
      stopRecording();
    }
    
    // Stop audio playback
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      setPlayingAudio(false);
    }
    
    // Reset all states
    setIsEmergency(false);
    setDescription('');
    setAlertSent(false);
    setAudioBlob(null);
    setRecordingTime(0);
    setStep('initial');
    clearInterval(recordingIntervalRef.current);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Success modal after alert sent
  if (alertSent && step === 'sent') {
    return (
      <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${className}`}>
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              🚨 {t('emergencyAlertSent', 'Emergency Alert Sent!')}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {t('emergencyProcessing', 'Your emergency alert with voice recording is being processed by FixMate emergency services. We are contacting 10111 emergency services on your behalf.')}
            </p>
            <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
              <p className="text-sm text-red-800 font-medium">
                ⚡ {t('emergencyActive', 'Emergency response is ACTIVE')}
              </p>
              <p className="text-xs text-red-600 mt-1">
                {t('stayOnLine', 'Please stay on the line and keep your phone accessible. Emergency services may contact you directly.')}
              </p>
            </div>
            {location && (
              <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-md mb-4">
                <p><strong>📍 Location:</strong> {location.address}</p>
                <p><strong>🗺️ Coordinates:</strong> {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}</p>
                {audioBlob && <p><strong>🎤 Voice Recording:</strong> {formatTime(recordingTime)} duration</p>}
                <p><strong>⏰ Time:</strong> {new Date().toLocaleString()}</p>
              </div>
            )}
            <div className="flex space-x-2">
              <button
                onClick={() => window.open('tel:10111', '_self')}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors font-medium"
              >
                📞 {t('call10111', 'Call 10111 Direct')}
              </button>
              <button
                onClick={handleCancel}
                className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                {t('close', 'Close')}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main emergency modal
  if (isEmergency) {
    return (
      <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${className}`}>
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="text-center mb-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              {step === 'processing' ? (
                <div className="w-8 h-8 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              )}
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              🚨 {t('emergencyAlert', 'Emergency Alert')}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {step === 'processing' 
                ? t('processingEmergency', 'Processing your emergency alert and contacting 10111...')
                : t('emergencyDescription', 'This will immediately alert FixMate emergency services who will contact 10111 on your behalf. Your location and voice message will be sent.')
              }
            </p>
          </div>

          {step !== 'processing' && (
            <>
              {/* Description */}
              <div className="mb-4">
                <label htmlFor="emergency-description" className="block text-sm font-medium text-gray-700 mb-2">
                  {t('whatIsHappening', 'What is happening?')} ({t('optional', 'Optional')})
                </label>
                <textarea
                  id="emergency-description"
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  placeholder={t('emergencyPlaceholder', 'Briefly describe the emergency situation...')}
                  disabled={isRecording}
                />
              </div>

              {/* Voice Recording Section */}
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  🎤 {t('voiceRecording', 'Voice Recording')} ({t('recommended', 'Recommended')})
                </h4>
                
                {!audioBlob && !isRecording && (
                  <button
                    onClick={startRecording}
                    className="w-full px-4 py-3 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors flex items-center justify-center space-x-2 font-medium"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                    </svg>
                    <span>{t('startRecording', 'Start Recording')}</span>
                  </button>
                )}

                {isRecording && (
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-3 mb-3">
                      <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
                      <span className="text-red-600 font-bold">{t('recording', 'Recording...')}</span>
                      <span className="text-lg font-mono bg-red-100 px-2 py-1 rounded text-red-700">
                        {formatTime(recordingTime)}
                      </span>
                    </div>
                    <button
                      onClick={stopRecording}
                      className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors font-medium"
                    >
                      ⏹️ {t('stopRecording', 'Stop Recording')}
                    </button>
                    <p className="text-xs text-gray-500 mt-2">
                      {t('maxRecordingTime', 'Maximum recording time: 2 minutes')}
                    </p>
                  </div>
                )}

                {audioBlob && !isRecording && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between bg-white p-3 rounded border">
                      <div className="flex items-center space-x-2">
                        <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm font-medium">{t('recordingComplete', 'Recording Complete')}</span>
                        <span className="text-sm text-gray-500">({formatTime(recordingTime)})</span>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={playRecording}
                        className="flex-1 px-3 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors flex items-center justify-center space-x-1"
                      >
                        {playingAudio ? (
                          <>
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                            <span>{t('pause', 'Pause')}</span>
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                            </svg>
                            <span>{t('play', 'Play')}</span>
                          </>
                        )}
                      </button>
                      <button
                        onClick={deleteRecording}
                        className="px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors flex items-center space-x-1"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        <span>{t('delete', 'Delete')}</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              onClick={handleCancel}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              disabled={loading || isRecording}
            >
              {t('cancel', 'Cancel')}
            </button>
            <button
              onClick={sendEmergencyAlert}
              disabled={loading || isRecording || step === 'processing'}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center font-medium"
            >
              {loading || step === 'processing' ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>{t('alerting', 'Sending Alert...')}</span>
                </div>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18.5c3.5-2 5.5-4.5 5.5-7.5 0-4.5-3-8-8-8s-8 3.5-8 8c0 3 2 5.5 5.5 7.5" />
                  </svg>
                  🚨 {t('sendEmergencyAlert', 'Send Emergency Alert')}
                </>
              )}
            </button>
          </div>

          <div className="mt-4 text-xs text-gray-500 text-center">
            <p>⚠️ {t('emergencyWarning', 'For immediate life-threatening danger, call 10111 directly')}</p>
            <button 
              onClick={() => window.open('tel:10111', '_self')}
              className="text-red-600 hover:text-red-800 font-medium underline mt-1"
            >
              📞 {t('callNow', 'Call 10111 Now')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main emergency button
  const buttonClasses = size === 'small' 
    ? 'bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md flex items-center space-x-1 text-sm font-medium transition-colors'
    : 'bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 font-medium transition-colors';

  return (
    <button
      onClick={handleEmergencyClick}
      className={`${buttonClasses} ${className}`}
      title={t('emergencyButtonTitle', 'Emergency - Get immediate help with voice recording')}
    >
      <svg className={size === 'small' ? 'w-4 h-4' : 'w-5 h-5'} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <span>{t('emergency', 'Emergency')}</span>
    </button>
  );
};

export default EmergencyButton;