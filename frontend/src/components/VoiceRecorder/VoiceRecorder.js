import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';

const VoiceRecorder = ({ onTranscription, onError, onClose }) => {
  const { t } = useLanguage();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [transcriptionResult, setTranscriptionResult] = useState('');
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
        transcribeAudio(audioBlob);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error starting recording:', error);
      onError(t('microphoneAccessError', 'Unable to access microphone. Please check permissions.'));
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');
      
      const response = await apiService.transcribeAudio(audioBlob);
      
      if (response.data && response.data.transcription) {
        setTranscriptionResult(response.data.transcription);
      } else if (response.data && response.data.detail) {
        setTranscriptionResult(response.data.detail);
      } else {
        onError(t('transcriptionFailed', 'Could not transcribe audio. Please try again.'));
      }
    } catch (error) {
      console.error('Transcription error:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        onError(`Error: ${error.response.data.detail}`);
      } else {
        onError(t('transcriptionError', 'Error processing audio. Please try again.'));
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendRecording = () => {
    if (transcriptionResult) {
      onTranscription(transcriptionResult);
      if (onClose) onClose();
    } else if (audioURL) {
      // If no transcription yet, try to transcribe the current audio
      const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
      transcribeAudio(audioBlob);
    }
  };

  const handleCancel = () => {
    clearRecording();
    if (onClose) onClose();
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const clearRecording = () => {
    setAudioURL(null);
    setRecordingTime(0);
    setTranscriptionResult('');
  };

  return (
    <div className="voice-recorder bg-white p-4 rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">{t('voiceRequest', 'Voice Request')}</h3>
        <span className="text-sm text-gray-500">
          {isRecording ? `${t('recording', 'Recording')}: ${formatTime(recordingTime)}` : t('readyToRecord', 'Ready to record')}
        </span>
      </div>

      <div className="flex items-center space-x-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={isProcessing}
            className="flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex items-center justify-center w-12 h-12 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors animate-pulse"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
            </svg>
          </button>
        )}

        <div className="flex-1">
          {isProcessing ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm text-gray-600">{t('processingAudio', 'Processing audio...')}</span>
            </div>
          ) : audioURL ? (
            <div className="flex items-center space-x-2">
              <audio controls src={audioURL} className="flex-1" />
              <button
                onClick={clearRecording}
                className="text-gray-500 hover:text-red-600 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              {isRecording ? 'Recording in progress...' : 'Click the microphone to start recording'}
            </p>
          )}
        </div>
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>💡 Tip:</strong> Speak clearly and describe your service needs. 
          Our AI understands multiple South African languages including English, Afrikaans, Zulu, and Xhosa.
        </p>
      </div>

      {/* Show transcription result if available */}
      {transcriptionResult && (
        <div className="mt-4 p-3 bg-green-50 rounded-md">
          <p className="text-sm text-green-800">
            <strong>✅ Transcription:</strong> {transcriptionResult}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-6 flex justify-end space-x-3">
        <button
          onClick={handleCancel}
          className="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleSendRecording}
          disabled={!audioURL || isProcessing}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isProcessing ? 'Processing...' : 'Send Recording'}
        </button>
      </div>
    </div>
  );
};

export default VoiceRecorder;