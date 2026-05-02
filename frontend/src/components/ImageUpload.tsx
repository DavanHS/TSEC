import { useState, useCallback } from 'react';
import { X, Image as ImageIcon } from 'lucide-react';

interface ImageUploadProps {
  onUpload: (imageData: string) => void;
}

export default function ImageUpload({ onUpload }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const processFile = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setPreview(result);
      const base64 = result.split(',')[1];
      onUpload(base64);
    };
    reader.readAsDataURL(file);
  }, [onUpload]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, [processFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  }, [processFile]);

  const clearImage = useCallback(() => {
    setPreview(null);
  }, []);

  return (
    <div className="w-full">
      {preview ? (
        <div className="relative rounded-lg overflow-hidden border">
          <img src={preview} alt="Preview" className="w-full h-40 object-cover" />
          <button
            onClick={clearImage}
            className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
            isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <label className="cursor-pointer">
            <input type="file" accept="image/*" onChange={handleInputChange} className="hidden" />
            <div className="flex flex-col items-center gap-2">
              <ImageIcon className="w-8 h-8 text-gray-400" />
              <p className="text-sm text-gray-600">Drop image or click to upload</p>
              <p className="text-xs text-gray-400">for visual search</p>
            </div>
          </label>
        </div>
      )}
    </div>
  );
}