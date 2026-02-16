import React, { useRef } from 'react';

/**
 * UploadArea – drag-and-drop zone for uploading files.
 *
 * Props:
 *   onFilesSelected – callback(FileList) when files are chosen or dropped
 */
export default function UploadArea({ onFilesSelected }) {
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    };

    const handleDragLeave = (e) => {
        e.currentTarget.classList.remove('dragover');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        onFilesSelected(e.dataTransfer.files);
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    const handleChange = (e) => {
        onFilesSelected(e.target.files);
        // Reset so the same file can be selected again
        e.target.value = '';
    };

    return (
        <div
            className="upload-area"
            onClick={handleClick}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            <div className="upload-content">
                <i className="fas fa-cloud-upload-alt"></i>
                <h3>Drop documents here</h3>
                <p>or <span className="browse-link">browse files</span></p>
                <small>Supports PDF, DOCX, TXT (max 10MB each)</small>
            </div>
            <input
                type="file"
                ref={fileInputRef}
                multiple
                accept=".pdf,.docx,.txt"
                hidden
                onChange={handleChange}
            />
        </div>
    );
}
