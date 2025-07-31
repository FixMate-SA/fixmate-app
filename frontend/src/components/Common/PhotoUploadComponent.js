import React, { useState, useRef } from 'react';

const PhotoUploadComponent = ({ 
  photoType = 'before', // 'before', 'after', 'progress'
  maxPhotos = 5,
  onPhotosChange,
  existingPhotos = [],
  disabled = false,
  required = false
}) => {
  const [photos, setPhotos] = useState(existingPhotos);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  const ACCEPTED_FORMATS = ['image/jpeg', 'image/png', 'image/gif'];

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    
    if (files.length + photos.length > maxPhotos) {
      setError(`Maximum ${maxPhotos} photos allowed`);
      return;
    }

    setUploading(true);
    setError('');

    try {
      const newPhotos = [];

      for (const file of files) {
        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
          setError(`Photo "${file.name}" is too large. Maximum size is 5MB.`);
          setUploading(false);
          return;
        }

        // Validate file type
        if (!ACCEPTED_FORMATS.includes(file.type)) {
          setError(`Photo "${file.name}" has unsupported format. Use JPEG, PNG, or GIF.`);
          setUploading(false);
          return;
        }

        // Convert to base64
        const base64 = await convertToBase64(file);
        
        newPhotos.push({
          id: `${Date.now()}_${Math.random()}`,
          data: base64,
          filename: file.name,
          size: file.size,
          type: file.type,
          description: ''
        });
      }

      const updatedPhotos = [...photos, ...newPhotos];
      setPhotos(updatedPhotos);
      
      if (onPhotosChange) {
        onPhotosChange(updatedPhotos);
      }

    } catch (err) {
      setError('Error processing photos. Please try again.');
      console.error('Photo processing error:', err);
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const removePhoto = (photoId) => {
    const updatedPhotos = photos.filter(photo => photo.id !== photoId);
    setPhotos(updatedPhotos);
    
    if (onPhotosChange) {
      onPhotosChange(updatedPhotos);
    }
  };

  const updatePhotoDescription = (photoId, description) => {
    const updatedPhotos = photos.map(photo =>
      photo.id === photoId ? { ...photo, description } : photo
    );
    setPhotos(updatedPhotos);
    
    if (onPhotosChange) {
      onPhotosChange(updatedPhotos);
    }
  };

  const getPhotoTypeIcon = () => {
    switch (photoType) {
      case 'before': return '📷';
      case 'after': return '✅';
      case 'progress': return '🔄';
      default: return '📸';
    }
  };

  const getPhotoTypeColor = () => {
    switch (photoType) {
      case 'before': return 'border-blue-300 bg-blue-50';
      case 'after': return 'border-green-300 bg-green-50';
      case 'progress': return 'border-yellow-300 bg-yellow-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{getPhotoTypeIcon()}</span>
          <h3 className="text-lg font-medium text-gray-900 capitalize">
            {photoType} Photos
            {required && <span className="text-red-500 ml-1">*</span>}
          </h3>
        </div>
        <div className="text-sm text-gray-500">
          {photos.length}/{maxPhotos} photos
        </div>
      </div>

      {/* Upload Area */}
      <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${getPhotoTypeColor()} ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-400'}`}>
        {!disabled && photos.length < maxPhotos && (
          <div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/jpeg,image/png,image/gif"
              onChange={handleFileSelect}
              className="hidden"
              disabled={disabled || uploading}
            />
            
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled || uploading}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Add {photoType} Photos</span>
                </>
              )}
            </button>
            
            <p className="mt-2 text-sm text-gray-600">
              Click to select up to {maxPhotos - photos.length} more photos
            </p>
            <p className="text-xs text-gray-500 mt-1">
              JPEG, PNG, GIF • Max 5MB each
            </p>
          </div>
        )}

        {photos.length >= maxPhotos && (
          <p className="text-sm text-gray-600">Maximum photos reached</p>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Photos Grid */}
      {photos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {photos.map((photo, index) => (
            <div key={photo.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                {/* Photo Preview */}
                <div className="flex-shrink-0">
                  <img
                    src={photo.data}
                    alt={`${photoType} ${index + 1}`}
                    className="w-20 h-20 object-cover rounded-md border border-gray-200"
                  />
                </div>

                {/* Photo Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {photo.filename}
                    </p>
                    {!disabled && (
                      <button
                        type="button"
                        onClick={() => removePhoto(photo.id)}
                        className="text-red-600 hover:text-red-800 transition-colors"
                        title="Remove photo"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>

                  <p className="text-xs text-gray-500 mb-2">
                    {(photo.size / 1024).toFixed(1)} KB • {photo.type.split('/')[1].toUpperCase()}
                  </p>

                  {/* Description Input */}
                  <textarea
                    value={photo.description}
                    onChange={(e) => updatePhotoDescription(photo.id, e.target.value)}
                    placeholder={`Describe this ${photoType} photo...`}
                    disabled={disabled}
                    rows={2}
                    className="w-full text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Guidelines */}
      {photos.length === 0 && !disabled && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">
            📋 {photoType.charAt(0).toUpperCase() + photoType.slice(1)} Photo Guidelines
          </h4>
          <ul className="text-sm text-blue-800 space-y-1">
            {photoType === 'before' && (
              <>
                <li>• Take clear photos of the problem area</li>
                <li>• Show the issue from multiple angles</li>
                <li>• Ensure good lighting for visibility</li>
                <li>• Include context of the surrounding area</li>
              </>
            )}
            {photoType === 'after' && (
              <>
                <li>• Show the completed work clearly</li>
                <li>• Take photos from the same angles as before photos</li>
                <li>• Demonstrate that the problem is resolved</li>
                <li>• Include any new parts or components installed</li>
              </>
            )}
            {photoType === 'progress' && (
              <>
                <li>• Document key stages of the work</li>
                <li>• Show tools and materials being used</li>
                <li>• Capture any discovered issues</li>
                <li>• Help client understand the process</li>
              </>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PhotoUploadComponent;