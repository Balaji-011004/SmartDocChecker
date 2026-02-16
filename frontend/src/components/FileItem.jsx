import React from 'react';
import { getFileIcon } from '../utils/helpers';

/**
 * FileItem – renders a single uploaded file with its name, size, and a remove button.
 *
 * Props:
 *   fileObj  – { id, file, name, size }
 *   onRemove – callback(id)
 */
export default function FileItem({ fileObj, onRemove }) {
    return (
        <div className="file-item">
            <div className="file-info">
                <div className="file-icon">
                    <i className={`fas ${getFileIcon(fileObj.file)}`}></i>
                </div>
                <div className="file-details">
                    <h4>{fileObj.name}</h4>
                    <p>{fileObj.size}</p>
                </div>
            </div>
            <button className="remove-file" onClick={() => onRemove(fileObj.id)}>
                <i className="fas fa-times"></i>
            </button>
        </div>
    );
}
