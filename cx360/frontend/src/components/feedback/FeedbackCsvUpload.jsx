import React, { useState, useRef } from 'react'; // Added useRef
import { uploadFeedbackCsv } from '../../services/feedbackService';

function FeedbackCsvUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null); // To help reset the file input

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadResult(null); // Clear previous results
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError('Please select a CSV file to upload.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setUploadResult(null);

    try {
      const result = await uploadFeedbackCsv(selectedFile);
      setUploadResult(result);
      if (result.successful_imports > 0 && onUploadSuccess) {
        onUploadSuccess(); // Callback to refresh feedback list if needed
      }
      // Clear the file input after successful or attempted upload
      if (fileInputRef.current) {
        fileInputRef.current.value = ""; // Reset file input
      }
      setSelectedFile(null); // Also reset state for selected file

    } catch (err) {
      console.error("CSV Upload error:", err);
      // err.message here will be the one thrown from service (already processed)
      setError(err.message || 'Failed to upload CSV.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="my-6 p-6 bg-white shadow-md rounded-lg border border-gray-200">
      <h3 className="text-xl font-semibold mb-4 text-gray-700">Import Feedback from CSV</h3>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="csvFile" className="block text-sm font-medium text-gray-700 mb-1">
            Choose CSV File:
          </label>
          <input
            type="file"
            id="csvFile"
            accept=".csv"
            onChange={handleFileChange}
            ref={fileInputRef} // Assign ref
            className="block w-full text-sm text-gray-600 border border-gray-300 rounded-md cursor-pointer
                       file:mr-4 file:py-2 file:px-4 file:rounded-l-md file:border-0
                       file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700
                       hover:file:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !selectedFile}
          className="w-full sm:w-auto px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Uploading...' : 'Upload CSV'}
        </button>
      </form>

      {error && <p className="text-red-500 mt-4 text-sm">Error: {error}</p>}

      {uploadResult && (
        <div className="mt-6 p-4 bg-gray-50 rounded-md border border-gray-200 text-sm">
          <h4 className="font-semibold text-gray-700 mb-2">Import Results:</h4>
          <p className="text-green-600">Successfully imported: {uploadResult.successful_imports} rows</p>
          <p className="text-red-600">Failed rows: {uploadResult.failed_rows}</p>
          {uploadResult.errors && uploadResult.errors.length > 0 && (
            <div className="mt-3">
              <h5 className="font-semibold text-gray-700 mb-1">Error Details:</h5>
              <ul className="list-disc list-inside max-h-48 overflow-y-auto text-xs bg-red-50 p-2 rounded-md">
                {uploadResult.errors.map((err, index) => (
                  <li key={index} className="text-red-700 my-1">
                    Row {err.row_number}: {err.error_message}
                    (Data: <pre className="inline whitespace-pre-wrap">{JSON.stringify(err.row_data)}</pre>)
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
export default FeedbackCsvUpload;
