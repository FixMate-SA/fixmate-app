import React, { useState, useRef, useEffect, memo } from 'react';
import { useInView } from 'react-intersection-observer';

// Optimized Image Component with lazy loading and WebP support
const OptimizedImage = memo(({
  src,
  alt = '',
  width,
  height,
  className = '',
  placeholder = 'blur',
  quality = 75,
  fallback = '/images/placeholder.jpg',
  onLoad,
  onError,
  ...props
}) => {
  const [imageSrc, setImageSrc] = useState(placeholder === 'blur' ? null : fallback);
  const [imageStatus, setImageStatus] = useState('loading');
  const [hasWebPSupport, setHasWebPSupport] = useState(null);
  const imgRef = useRef(null);

  // Intersection observer for lazy loading
  const { ref: inViewRef, inView } = useInView({
    threshold: 0,
    rootMargin: '50px 0px', // Start loading 50px before image comes into view
    triggerOnce: true,
  });

  // Check WebP support
  useEffect(() => {
    const checkWebPSupport = () => {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      const webPSupported = canvas.toDataURL('image/webp').indexOf('image/webp') === 5;
      setHasWebPSupport(webPSupported);
    };

    if (hasWebPSupport === null) {
      checkWebPSupport();
    }
  }, [hasWebPSupport]);

  // Generate optimized image URL
  const getOptimizedImageUrl = (originalSrc, width, height, quality) => {
    // If it's a base64 image, return as-is
    if (originalSrc?.startsWith('data:')) {
      return originalSrc;
    }

    // If it's already optimized or external URL, return as-is
    if (!originalSrc?.startsWith('/') || originalSrc.includes('?')) {
      return originalSrc;
    }

    // Create optimized URL with parameters
    const params = new URLSearchParams();
    if (width) params.set('w', width.toString());
    if (height) params.set('h', height.toString());
    if (quality) params.set('q', quality.toString());
    if (hasWebPSupport) params.set('format', 'webp');

    return `${originalSrc}?${params.toString()}`;
  };

  // Load image when in view
  useEffect(() => {
    if (inView && src && imageStatus === 'loading') {
      const optimizedSrc = getOptimizedImageUrl(src, width, height, quality);
      
      const img = new Image();
      
      img.onload = () => {
        setImageSrc(optimizedSrc);
        setImageStatus('loaded');
        onLoad?.(img);
      };
      
      img.onerror = () => {
        setImageSrc(fallback);
        setImageStatus('error');
        onError?.(new Error(`Failed to load image: ${optimizedSrc}`));
      };
      
      img.src = optimizedSrc;
    }
  }, [inView, src, width, height, quality, hasWebPSupport, fallback, onLoad, onError, imageStatus]);

  // Generate placeholder based on type
  const getPlaceholder = () => {
    if (placeholder === 'blur') {
      return (
        <div 
          className={`bg-gray-200 animate-pulse flex items-center justify-center ${className}`}
          style={{ width, height, minHeight: height || 200 }}
        >
          <svg
            className="w-8 h-8 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      );
    }
    
    if (placeholder === 'empty') {
      return (
        <div 
          className={`bg-gray-100 flex items-center justify-center ${className}`}
          style={{ width, height, minHeight: height || 200 }}
        >
          <span className="text-gray-400 text-sm">Image</span>
        </div>
      );
    }
    
    return null;
  };

  // Combine refs for intersection observer
  const setRefs = (element) => {
    imgRef.current = element;
    inViewRef(element);
  };

  return (
    <div className="relative overflow-hidden">
      {/* Show placeholder while loading */}
      {imageStatus === 'loading' && getPlaceholder()}
      
      {/* Show image when loaded */}
      {imageSrc && imageStatus !== 'loading' && (
        <img
          ref={setRefs}
          src={imageSrc}
          alt={alt}
          width={width}
          height={height}
          className={`transition-opacity duration-300 ${
            imageStatus === 'loaded' ? 'opacity-100' : 'opacity-0'
          } ${className}`}
          loading="lazy"
          {...props}
        />
      )}
      
      {/* Error state */}
      {imageStatus === 'error' && (
        <div 
          className={`bg-red-50 border border-red-200 flex items-center justify-center ${className}`}
          style={{ width, height, minHeight: height || 200 }}
        >
          <div className="text-center text-red-600">
            <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.732 15.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span className="text-sm">Failed to load</span>
          </div>
        </div>
      )}
    </div>
  );
});

OptimizedImage.displayName = 'OptimizedImage';

// Progressive Image Component for hero images and large visuals
const ProgressiveImage = memo(({
  src,
  lowQualitySrc,
  alt = '',
  className = '',
  ...props
}) => {
  const [currentSrc, setCurrentSrc] = useState(lowQualitySrc);
  const [isHighQualityLoaded, setIsHighQualityLoaded] = useState(false);

  useEffect(() => {
    if (src) {
      const img = new Image();
      img.onload = () => {
        setCurrentSrc(src);
        setIsHighQualityLoaded(true);
      };
      img.src = src;
    }
  }, [src]);

  return (
    <div className="relative overflow-hidden">
      <OptimizedImage
        src={currentSrc}
        alt={alt}
        className={`transition-all duration-500 ${
          isHighQualityLoaded ? 'filter-none' : 'filter blur-sm'
        } ${className}`}
        {...props}
      />
      
      {!isHighQualityLoaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse opacity-30" />
      )}
    </div>
  );
});

ProgressiveImage.displayName = 'ProgressiveImage';

// Image Gallery Component with lazy loading
const OptimizedImageGallery = memo(({ images = [], className = '', onImageClick }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  const handleImageClick = (image, index) => {
    setSelectedImage({ ...image, index });
    onImageClick?.(image, index);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const navigateImage = (direction) => {
    if (!selectedImage) return;
    
    const newIndex = direction === 'next' 
      ? (selectedImage.index + 1) % images.length
      : (selectedImage.index - 1 + images.length) % images.length;
    
    setSelectedImage({ ...images[newIndex], index: newIndex });
  };

  return (
    <>
      <div className={`grid gap-4 ${className}`}>
        {images.map((image, index) => (
          <div
            key={image.id || index}
            className="relative group cursor-pointer overflow-hidden rounded-lg"
            onClick={() => handleImageClick(image, index)}
          >
            <OptimizedImage
              src={image.src || image.url}
              alt={image.alt || `Image ${index + 1}`}
              width={300}
              height={200}
              className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
              placeholder="blur"
            />
            
            {/* Overlay */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
              <svg 
                className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
              </svg>
            </div>
          </div>
        ))}
      </div>

      {/* Modal for full-size image */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
          <div className="relative max-w-4xl max-h-full">
            <OptimizedImage
              src={selectedImage.src || selectedImage.url}
              alt={selectedImage.alt || `Image ${selectedImage.index + 1}`}
              className="max-w-full max-h-full object-contain"
              placeholder="blur"
            />
            
            {/* Navigation */}
            {images.length > 1 && (
              <>
                <button
                  onClick={() => navigateImage('prev')}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <button
                  onClick={() => navigateImage('next')}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </>
            )}
            
            {/* Close button */}
            <button
              onClick={closeModal}
              className="absolute top-4 right-4 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            {/* Image counter */}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
              {selectedImage.index + 1} / {images.length}
            </div>
          </div>
        </div>
      )}
    </>
  );
});

OptimizedImageGallery.displayName = 'OptimizedImageGallery';

export { OptimizedImage, ProgressiveImage, OptimizedImageGallery };
export default OptimizedImage;